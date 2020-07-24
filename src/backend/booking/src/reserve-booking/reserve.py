import datetime
import os
import uuid

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from botocore.exceptions import ClientError

from process_booking import process_booking_handler

logger = Logger()
tracer = Tracer()
metrics = Metrics()

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table_name = os.getenv("BOOKING_TABLE_NAME", "undefined")
table = dynamodb.Table(table_name)


class BookingReservationException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Booking reservation failed"
        self.details = details or {}


def is_booking_request_valid(booking):
    return all(x in booking for x in ["outboundFlightId", "customerId", "chargeId"])


@tracer.capture_method
def reserve_booking(booking):
    """Creates a new booking as UNCONFIRMED

    Parameters
    ----------
    booking: dict
        chargeId: string
            pre-authorization charge ID

        stateExecutionId: string
            Step Functions Process Booking Execution ID

        chargeId: string
            Pre-authorization payment token

        customer: string
            Customer unique identifier

        bookingOutboundFlightId: string
            Outbound flight unique identifier

    Returns
    -------
    dict
        bookingId: string
    """
    try:
        booking_id = str(uuid.uuid4())
        state_machine_execution_id = booking["name"]
        outbound_flight_id = booking["outboundFlightId"]
        customer_id = booking["customerId"]
        payment_token = booking["chargeId"]

        booking_item = {
            "id": booking_id,
            "stateExecutionId": state_machine_execution_id,
            "__typename": "Booking",
            "bookingOutboundFlightId": outbound_flight_id,
            "checkedIn": False,
            "customer": customer_id,
            "paymentToken": payment_token,
            "status": "UNCONFIRMED",
            "createdAt": str(datetime.datetime.now()),
        }

        logger.debug(
            {"operation": "reserve_booking", "details": {"outbound_flight_id": outbound_flight_id}}
        )
        ret = table.put_item(Item=booking_item)

        logger.info({"operation": "reserve_booking", "details": ret})
        tracer.put_metadata(booking_id, booking_item, "booking")

        return {"bookingId": booking_id}
    except ClientError as err:
        logger.exception({"operation": "reserve_booking"})
        raise BookingReservationException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@process_booking_handler(logger=logger)
def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to reserve a booking

    Parameters
    ----------
    event: dict, required
        Step Functions State Machine event

        chargeId: string
            pre-authorization charge ID

        stateExecutionId: string
            Step Functions Process Booking Execution ID

        chargeId: string
            Pre-authorization payment token

        customerId: string
            Customer unique identifier

        bookingOutboundFlightId: string
            Outbound flight unique identifier

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    -------
    bookingId: string
        booking ID generated

    Raises
    ------
    BookingReservationException
        Booking Reservation Exception including error message upon failure
    """
    if not is_booking_request_valid(event):
        metrics.add_metric(name="InvalidReservationRequest", unit=MetricUnit.Count, value=1)
        logger.error({"operation": "input_validation", "details": event})
        raise ValueError("Invalid booking request")

    try:
        logger.debug(f"Reserving booking for customer {event['customerId']}")
        ret = reserve_booking(event)

        metrics.add_metric(name="SuccessfulReservation", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("Booking", ret["bookingId"])
        tracer.put_annotation("BookingStatus", "RESERVED")

        # Step Functions use the return to append `bookingId` key into the overall output
        return ret["bookingId"]
    except BookingReservationException as err:
        metrics.add_metric(name="FailedReservation", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingStatus", "ERROR")
        logger.exception({"operation": "reserve_booking"})
        raise
