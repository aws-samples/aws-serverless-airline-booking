import functools
import logging
import os
from dataclasses import dataclass
from distutils.util import strtobool
from typing import Any, Callable, Dict

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import models

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
is_trace_disabled = strtobool(os.getenv("DISABLE_TRACE", False))


@dataclass
class Tracer:
    service: str
    is_disabled: bool = is_trace_disabled
    is_cold_start: bool = True
    modules_to_patch: tuple = ("boto3", "requests")
    provider: xray_recorder = xray_recorder
    """Tracer using AWS-XRay to provide decorators with known Airline defaults for Lambda functions

    When running locally, it honours DISABLE_TRACE environment variable
    so end user code doesn't have to be modified to run it locally
    instead Tracer returns dummy segments/subsegments.

    It also patches boto3 and requests modules by default
    and optionally accepts a tuple of modules to patch if necessary

    Example
    -------
    A Lambda function using Tracer

        >>> from lambda_python_powertools.tracing import Tracer
        >>> tracer = Tracer(service="greeting")

        >>> @tracer.capture_method
        >>> def greeting(name: str) -> Dict:
                return {
                    "name": name
                }

        >>> @tracer.capture_lambda_handler
        >>> def handler(event: dict, context: Any) -> Dict:
            >>> print("Received event from Lambda...")
            >>> response = greeting(name="Heitor")
            >>> return response

    Booking Lambda function using Tracer that adds additional annotation/metadata

        >>> from lambda_python_powertools.tracing import Tracer
        >>> tracer = Tracer(service="booking")

        >>> @tracer.capture_method
        >>> def confirm_booking(booking_id: str) -> Dict:
                resp = add_confirmation(booking_id)

                tracer.put_annotation("BookingConfirmation", resp['requestId'])
                tracer.put_metadata("Booking confirmation", resp)

                return resp

        >>> @tracer.capture_lambda_handler
        >>> def handler(event: dict, context: Any) -> Dict:
            >>> print("Received event from Lambda...")
            >>> response = greeting(name="Heitor")
            >>> return response

    A Lambda function using Tracer disabled for running it locally

        >>> export DISABLE_TRACE="true"
        >>> from lambda_python_powertools.tracing import Tracer
        >>> tracer = Tracer(service="booking")

        >>> @tracer.capture_lambda_handler
        >>> def handler(event: dict, context: Any) -> Dict:
            >>> print("Received event from Lambda...")
            >>> response = greeting(name="Lessa")
            >>> return response

    Parameters
    ----------
    service: str
        Service name that will be appended in all tracing metadata
    is_disabled: bool
        Flag to disable tracing, useful when running locally. Use DISABLE_TRACE="true" instead
    modules_to_patch: tuple
        Tuple with supported modules to patch
        Reference: https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference/thirdparty.html

    Returns
    -------
    Tracer
        Tracer instance with imported modules patched
    """

    def __post_init__(self):
        logger.debug("Patching modules...")
        self.__patch(self.modules_to_patch)

    def capture_lambda_handler(
        self, lambda_handler: Callable[[Dict, Any], Any] = None, process_booking_sfn: bool = False
    ):
        """Decorator to create subsegment for lambda handlers

        As Lambda follows (event, context) signature we can remove some of the boilerplate
        Also, Process Booking State Machine annotations are standard
        across all Lambdas, and we can hide that boilerplate in here
        and also capture any exception any Lambda function throws or its response as metadata

        Example
        -------
        Lambda function using capture_lambda_handler decorator

            >>> tracer = Tracer(service="payment")
            >>> @tracer.capture_lambda_handler
                def handler(event, context)

        Lambda function that is part of Process Booking State Machine

            >>> tracer = Tracer(service="payment", process_booking_sfn=True)
            >>> @tracer.capture_lambda_handler
                def handler(event, context)

        Parameters
        ----------
        method : Callable
            Method to annotate on

        Raises
        ------
        err
            Exception raised by method
        """

        # If handler is None we've been called with a service name
        # We then return a partial function with args filled
        # Next time we're called we'll call our Lambda
        # This allows us to avoid writing wrapper_wrapper type of fn
        if lambda_handler is None:
            logger.debug("Decorator called with parameters")
            logger.debug(f"process booking sfn: {process_booking_sfn}")
            return functools.partial(
                self.capture_lambda_handler, process_booking_sfn=process_booking_sfn
            )

        @functools.wraps(lambda_handler)
        def decorate(event, context):
            self.__create_subsegment(name=f"## {lambda_handler.__name__}")

            if process_booking_sfn:
                self.__capture_process_booking_state_machine(event=event)

            try:
                logger.debug("Calling lambda handler")
                response = lambda_handler(event, context)
                logger.debug("Received lambda handler response successfully")
                logger.debug(response)
                if response:
                    self.put_metadata("lambda handler response", response)
            except Exception as err:
                logger.debug("Exception received from lambda handler")
                self.put_metadata(f"{self.service}_error", err)
                raise err
            finally:
                self.__end_subsegment()

            return response

        return decorate

    def capture_method(self, method: Callable = None):
        """Decorator to create subsegment for arbitrary functions

        It also captures both response and exceptions as metadata

        Example
        -------
        Custom function using capture_method decorator

            >>> tracer = Tracer(service="payment")

            >>> @tracer.capture_method
                def some_function()

        Parameters
        ----------
        method : Callable
            Method to annotate on

        Raises
        ------
        err
            Exception raised by method
        """

        @functools.wraps(method)
        def decorate(*args, **kwargs):
            method_name = f"{method.__name__}"
            self.__create_subsegment(name=f"## {method_name}")

            try:
                logger.debug(f"Calling method: {method_name}")
                response = method(*args, **kwargs)
                logger.debug(f"Received {method_name} response successfully")
                logger.debug(response)
                if response is not None:
                    self.put_metadata(f"{method_name} response", response)
            except Exception as err:
                logger.debug(f"Exception received from '{method_name}'' method")
                self.put_metadata(f"{method_name} error", err)
                raise err
            finally:
                self.__end_subsegment()

            return response

        return decorate

    def put_annotation(self, key: str, value: Any):
        """Adds annotation to existing segment or subsegment

        Example
        -------
        Custom annotation for a pseudo service named payment

            >>> tracer = Tracer(service="payment")
            >>> tracer.put_annotation("PaymentStatus", "CONFIRMED")

        Parameters
        ----------
        key : str
            Annotation key (e.g. PaymentStatus)
        value : Any
            Value for annotation (e.g. "CONFIRMED")
        """
        # Will no longer be needed once #155 is resolved
        # https://github.com/aws/aws-xray-sdk-python/issues/155
        if self.is_disabled:
            return

        logger.debug(f"Annotating on key '{key}'' with '{value}''")
        self.provider.put_annotation(key=key, value=value)

    def put_metadata(self, key: str, value: object, namespace: str = None):
        """Adds metadata to existing segment or subsegment

        Parameters
        ----------
        key : str
            Metadata key
        value : object
            Value for metadata
        namespace : str, optional
            Namespace that metadata will lie under, by default None

        Example
        -------
        Custom metadata for a pseudo service named payment

            >>> tracer = Tracer(service="payment")
            >>> response = collect_payment()
            >>> tracer.put_metadata("Payment collection", response)
        """
        # Will no longer be needed once #155 is resolved
        # https://github.com/aws/aws-xray-sdk-python/issues/155
        if self.is_disabled:
            return

        _namespace = namespace or self.service
        logger.debug(f"Adding metadata on key '{key}'' with '{value}'' at namespace '{namespace}''")
        self.provider.put_metadata(key=key, value=value, namespace=_namespace)

    def __capture_process_booking_state_machine(self, event: Dict = None):
        """Captures process booking state machine input for annotation and metadata

        Parameters
        ----------
        event : dict
            Process Booking State Machine
        """
        if event is None:
            logger.debug("No event to be captured")
            return

        logger.debug("Capturing input from process booking state machine")
        logger.debug(event)

        customer_id = event.get("customerId", "UNDEFINED")
        booking_id = event.get("bookingId", "UNDEFINED")
        charge_id = event.get("chargeId", "UNDEFINED")
        outbound_flight_id = event.get("outboundFlightId", "UNDEFINED")
        state_machine_execution_id = event.get("name", "UNDEFINED")

        logger.debug("Annotating process booking state machine data into subsegment")
        self.put_annotation("Payment", charge_id)
        self.put_annotation("Booking", booking_id)
        self.put_annotation("Customer", customer_id)
        self.put_annotation("Flight", outbound_flight_id)
        self.put_annotation("StateMachineExecution", state_machine_execution_id)

    def __create_subsegment(self, name: str) -> models.subsegment:
        """Creates subsegment or a dummy segment plus subsegment if tracing is disabled

        It also assumes Tracer would be instantiated statically so that cold starts are captured.

        Parameters
        ----------
        name : str
            Subsegment name

        Example
        -------
        Creates a genuine subsegment

            >>> self.__create_subsegment(name="a meaningful name")

        Returns
        -------
        models.subsegment
            AWS X-Ray Subsegment
        """
        # Will no longer be needed once #155 is resolved
        # https://github.com/aws/aws-xray-sdk-python/issues/155
        subsegment = None

        if self.is_disabled:
            logger.debug("Tracing has been disabled, return dummy subsegment instead")
            segment = models.dummy_entities.DummySegment()
            subsegment = models.dummy_entities.DummySubsegment(segment)
        else:
            subsegment = self.provider.begin_subsegment(name=name)
            if self.is_cold_start:
                logger.debug("Annotating cold start")
                subsegment.put_annotation("ColdStart", True)
                self.is_cold_start = False

        return subsegment

    def __end_subsegment(self):
        """Ends an existing subsegment

        Parameters
        ----------
        subsegment : models.subsegment
            Subsegment previously created
        """
        if self.is_disabled:
            logger.debug("Tracing has been disabled, return instead")
            return

        self.provider.end_subsegment()

    def __patch(self, modules: tuple):
        """Patch modules for instrumentation

        Parameters
        ----------
        modules : tuple
            Tuple with modules to be patched
        """
        if self.is_disabled:
            logger.debug("Tracing has been disabled, aborting patch")
            return

        from aws_xray_sdk.core import patch

        patch(modules)
