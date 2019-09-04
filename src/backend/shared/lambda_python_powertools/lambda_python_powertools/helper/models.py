"""Collection of classes as models and builder functions
that provide classes as data representation for
key data used in more than one place.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union


@dataclass
class LambdaContextModel:
    """A handful of Lambda Runtime Context fields

    Full Lambda Context object: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    NOTE
    ----

    Originally, memory_size is `int` but we cast to `str` in this model
    due to aws_lambda_logging library use of `%` during formatting
    Ref: https://gitlab.com/hadrien/aws_lambda_logging/blob/master/aws_lambda_logging.py#L47

    Parameters
    ----------
    function_name: str
        Lambda function name, by default "UNDEFINED"
        e.g. "test"
    function_memory_size: str
        Lambda function memory in MB, by default "UNDEFINED"
        e.g. "128"
        casting from int to str due to aws_lambda_logging using `%` when enumerating fields
    function_arn: str
        Lambda function ARN, by default "UNDEFINED"
        e.g. "arn:aws:lambda:eu-west-1:809313241:function:test"
    function_request_id: str
        Lambda function unique request id, by default "UNDEFINED"
        e.g. "52fdfc07-2182-154f-163f-5f0f9a621d72"
    """

    function_name: str = "UNDEFINED"
    function_memory_size: str = "UNDEFINED"
    function_arn: str = "UNDEFINED"
    function_request_id: str = "UNDEFINED"


@dataclass
class ProcessBookingModel:
    """Process Booking State Machine Input model

    Selection of important keys used across logging and tracing

    Parameters
    ----------
    customer_id: str
        Unique customer identifier, by default "UNDEFINED"
    booking_id: str
        Unique booking identifier, by default "UNDEFINED"
    charge_id: str
        Payment token identifier, by default "UNDEFINED"
    outbound_flight_id: str
        Unique flight identifier, by default "UNDEFINED"
    state_machine_execution_id: str
        Unique process booking state machine execution identifier, by default "UNDEFINED"
    """

    outbound_flight_id: str = "UNDEFINED"
    customer_id: str = "UNDEFINED"
    charge_id: str = "UNDEFINED"
    state_machine_execution_id: str = "UNDEFINED"
    booking_id: str = "UNDEFINED"


def build_process_booking_model(event: Dict) -> ProcessBookingModel:
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
    ProcessBookingModel
        Process Booking state machine
    """
    context = {
        "customer_id": event.get("customerId"),
        "booking_id": event.get("bookingId"),
        "charge_id": event.get("chargeId"),
        "outbound_flight_id": event.get("outboundFlightId"),
        "state_machine_execution_id": event.get("name"),
    }

    return ProcessBookingModel(**context)


def build_lambda_context_model(context: object) -> LambdaContextModel:
    """Captures Lambda function runtime info to be used across all log statements

    Parameters
    ----------
    context : object
        Lambda context object

    Returns
    -------
    LambdaContextModel
        Lambda context only with select fields
    """

    context = {
        "function_name": context.function_name,
        "function_memory_size": str(context.memory_limit_in_mb),
        "function_arn": context.invoked_function_arn,
        "function_request_id": context.aws_request_id,
    }

    return LambdaContextModel(**context)


class MetricUnit(Enum):
    Seconds = "Seconds"
    Microseconds = "Microseconds"
    Milliseconds = "Milliseconds"
    Bytes = "Bytes"
    Kilobytes = "Kilobytes"
    Megabytes = "Megabytes"
    Gigabytes = "Gigabytes"
    Terabytes = "Terabytes"
    Bits = "Bits"
    Kilobits = "Kilobits"
    Megabits = "Megabits"
    Gigabits = "Gigabits"
    Terabits = "Terabits"
    Percent = "Percent"
    Count = "Count"
    BytesPerSecond = "Second"
    KilobytesPerSecond = "Second"
    MegabytesPerSecond = "Second"
    GigabytesPerSecond = "Second"
    TerabytesPerSecond = "Second"
    BitsPerSecond = "Second"
    KilobitsPerSecond = "Second"
    MegabitsPerSecond = "Second"
    GigabitsPerSecond = "Second"
    TerabitsPerSecond = "Second"
    CountPerSecond = "Second"


def build_metric_unit_from_str(unit: Union[str, MetricUnit]) -> MetricUnit:
    """Builds correct metric unit value from string or return Count as default

    Parameters
    ----------
    unit : str, MetricUnit
        metric unit

    Returns
    -------
    MetricUnit
        Metric Unit enum from string value or MetricUnit.Count as a default
    """
    if isinstance(unit, MetricUnit):
        return unit

    if isinstance(unit, str):
        unit = unit.lower().capitalize()

    metric_unit = None

    try:
        metric_unit = MetricUnit[unit]
    except (TypeError, KeyError):
        metric_units = [units for units, _ in MetricUnit.__members__.items()]
        raise ValueError(
            f"Invalid Metric Unit - Received {unit}. Value Metric Units are {metric_units}"
        )

    return metric_unit
