from typing import Any, Callable, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

from .models import ProcessBookingModel, ProcessBookingState


@lambda_handler_decorator(trace_execution=True)
def process_booking_handler(
    handler: Callable, event: Dict, context: Any, logger: Logger = None
) -> Callable:
    """Injects process booking SFN data into logger as an annotation

    Parameters
    ----------
    handler : Callable
        Lambda fn handler
    event : Dict
        Lambda fn event 
    context : Any
        Lambda fn context object
    logger : Logger, optional
        Existing Powertools Logger, by default None

    Returns
    -------
    Callable
        Lambda fn handler
    """
    if logger is None:
        logger = Logger()

    handler = logger.inject_lambda_context(handler)
    process_booking_context = _build_process_booking_model(event)

    logger.info("Injecting and annotating process booking state machine")
    _logger_inject_process_booking_sfn(logger=logger, event=event)
    _tracer_annotate_process_booking_sfn(
        process_booking_context=process_booking_context
    )

    return handler(event, context)


def _logger_inject_process_booking_sfn(logger: Logger, event: Dict):
    """Injects process booking state machine input into existing Logger

    Parameters
    ----------
    logger : Logger
        Lambda application Logger
    event : Dict
        Lambda event
    """
    process_booking_context = _build_process_booking_model(event)
    logger.structure_logs(append=True, **process_booking_context.__dict__)


def _tracer_annotate_process_booking_sfn(process_booking_context: ProcessBookingState):
    """Captures process booking state machine input for annotation and metadata

    Parameters
    ----------
    event : ProcessBookingState
        Process Booking State Machine
    """
    tracer = Tracer(auto_patch=False)
    tracer.put_annotation("Payment", process_booking_context.charge_id)
    tracer.put_annotation("Booking", process_booking_context.booking_id)
    tracer.put_annotation("Customer", process_booking_context.customer_id)
    tracer.put_annotation("Flight", process_booking_context.outbound_flight_id)
    tracer.put_annotation(
        "StateMachineExecution", process_booking_context.state_machine_execution_id
    )


def _build_process_booking_model(event: Dict) -> ProcessBookingState:
    """Collects important fields from Process Booking State Machine
    and returns a object with default values if they're not present.

    Parameters
    ----------
    event : Dict
        Process Booking state machine input

        customer_id: string
            Unique customer identifier
        booking_id: string
            Unique booking identifier
        charge_id: string
            Payment token identifier
        outbound_flight_id: string
            Unique flight identifier
        state_machine_execution_id: string
            Unique process booking state machine execution identifier

    Returns
    -------
    ProcessBookingState
        Process Booking state machine
    """
    context = {
        "customer_id": event.get("customerId", ""),
        "booking_id": event.get("bookingId", ""),
        "charge_id": event.get("chargeId", ""),
        "outbound_flight_id": event.get("outboundFlightId", ""),
        "state_machine_execution_id": event.get("name", ""),
    }

    return ProcessBookingModel(**context)
