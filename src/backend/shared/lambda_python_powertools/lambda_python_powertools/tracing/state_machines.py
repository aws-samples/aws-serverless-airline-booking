import functools
import os
import logging

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.models.dummy_entities import DummySubsegment, DummySegment

logging.basicConfig(
    format="%(funcName)s:%(lineno)d - %(asctime)s - %(message)s",
    level=os.getenv("LOG_LEVEL", logging.INFO),
)
is_trace_disabled = os.getenv("DISABLE_TRACE", 0)


def capture_lambda_handler(
    lambda_handler=None, service=None, client=None, process_booking_sfn=False
):
    # If handler is None we've been called with a service name
    # We then return a partial function with service filled
    # Next time we're called we'll call our Lambda
    # This allows us to avoid writing wrapper_wrapper type of fn
    if lambda_handler is None:
        logging.debug("Decorator called with parameters")
        logging.debug(f"service: {service}")
        logging.debug(f"client: {client}")
        logging.debug(f"process booking sfn: {process_booking_sfn}")
        return functools.partial(
            capture_lambda_handler,
            service=service,
            client=client,
            process_booking_sfn=process_booking_sfn,
        )

    if client is None:
        client = xray_recorder

    @functools.wraps(lambda_handler)
    def decorate(event, context):
        subsegment = _create_subsegment(
            name=f"## {lambda_handler.__name__}", client=client
        )

        if process_booking_sfn:
            capture_process_booking_state_machine(
                event=event, subsegment=subsegment, client=client
            )

        try:
            context.tracer = subsegment
            logging.debug("Calling lambda handler")
            response = lambda_handler(event, context)
            logging.debug("Received lambda handler response successfully")
            logging.debug(response)
        except Exception as err:
            logging.debug("Exception received from lambda handler")
            subsegment.put_metadata(f"{service}_error", err, f"{service}")
            raise err
        finally:
            _end_subsegment(subsegment)

        return response

    return decorate


def capture_process_booking_state_machine(event=None, subsegment=None, client=None):
    if subsegment is None or client is None:
        logging.debug("Subsegment or client are None; aborting...")
        return

    if event is not None:
        logging.debug("Capturing input from process booking state machine")
        logging.debug(event)
        customer_id = event.get("customerId", "UNDEFINED")
        booking_id = event.get("bookingId", "UNDEFINED")
        charge_id = event.get("chargeId", "UNDEFINED")
        outbound_flight_id = event.get("outboundFlightId", "UNDEFINED")
        state_machine_execution_id = event.get("name", "UNDEFINED")

    logging.debug("Annotating process booking state machine data into subsegment")
    subsegment.put_annotation("Payment", charge_id)
    subsegment.put_annotation("Booking", booking_id)
    subsegment.put_annotation("Customer", customer_id)
    subsegment.put_annotation("Flight", outbound_flight_id)
    subsegment.put_annotation("StateMachineExecution", state_machine_execution_id)


# Will no longer be needed once #155 is resolved
# https://github.com/aws/aws-xray-sdk-python/issues/155
def _create_subsegment(name=None, client=None):
    if is_trace_disabled:
        logging.debug("Tracing has been disabled, return dummy subsegment instead")
        segment = DummySegment()
        subsegment = DummySubsegment(segment)
    else:
        subsegment = client.begin_subsegment(name=name)

    return subsegment


def _end_subsegment(subsegment):
    if is_trace_disabled:
        logging.debug("Tracing has been disabled, return instead")
        return

    subsegment.end_subsegment()
