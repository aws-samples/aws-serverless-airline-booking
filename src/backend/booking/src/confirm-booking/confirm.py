import os
import secrets

import boto3
from botocore.exceptions import ClientError

from lambda_python_powertools.logging import (
    MetricUnit,
    log_metric,
    logger_inject_process_booking_sfn,
    logger_setup,
)
from lambda_python_powertools.tracing import Tracer

logger = logger_setup()
tracer = Tracer()

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table_name = os.getenv("BOOKING_TABLE_NAME", "undefined")
table = dynamodb.Table(table_name)

_cold_start = True


class BookingConfirmationException(Exception):
    def __init__(self, message=None, status_code=None, details=None):

        super(BookingConfirmationException, self).__init__()

        self.message = message or "Booking confirmation failed"
        self.status_code = status_code or 500
        self.details = details or {}


@tracer.capture_method
def confirm_booking(booking_id):
    """Update existing booking to CONFIRMED and generates a Booking reference

    Parameters
    ----------
    booking_id : string
        Unique Booking ID

    Returns
    -------
    dict
        bookingReference: string

    Raises
    ------
    BookingConfirmationException
        Booking Confirmation Exception including error message upon failure
    """
    try:
        logger.debug({"operation": "confirm_booking", "details": {"booking_id": booking_id}})
        reference = secrets.token_urlsafe(4)
        ret = table.update_item(
            Key={"id": booking_id},
            ConditionExpression="id = :idVal",
            UpdateExpression="SET bookingReference = :br, #STATUS = :confirmed",
            ExpressionAttributeNames={"#STATUS": "status"},
            ExpressionAttributeValues={
                ":br": reference,
                ":idVal": booking_id,
                ":confirmed": "CONFIRMED",
            },
            ReturnValues="UPDATED_NEW",
        )

        logger.info({"operation": "confirm_booking", "details": ret})
        logger.debug("Adding update item operation result as tracing metadata")
        tracer.put_metadata(booking_id, ret)

        return {"bookingReference": reference}
    except ClientError as err:
        logger.debug({"operation": "confirm_booking", "details": err})
        raise BookingConfirmationException(details=err)


@tracer.capture_lambda_handler(process_booking_sfn=True)
@logger_inject_process_booking_sfn
def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to confirm booking

    Parameters
    ----------
    event: dict, required
        Step Functions State Machine event

        bookingId: string
            Unique Booking ID of an unconfirmed booking

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    -------
    string
        bookingReference generated

    Raises
    ------
    BookingConfirmationException
        Booking Confirmation Exception including error message upon failure
    """

    global _cold_start
    if _cold_start:
        log_metric(
            name="ColdStart", unit=MetricUnit.Count, value=1, function_name=context.function_name
        )
        _cold_start = False

    booking_id = event.get("bookingId")
    if not booking_id:
        log_metric(
            name="InvalidBookingRequest",
            unit=MetricUnit.Count,
            value=1,
            operation="confirm_booking",
        )
        logger.error({"operation": "invalid_event", "details": event})
        raise ValueError("Invalid booking ID")

    try:
        logger.debug(f"Confirming booking - {booking_id}")
        ret = confirm_booking(booking_id)

        log_metric(name="SuccessfulBooking", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Status annotation")
        tracer.put_annotation("BookingReference", ret["bookingReference"])
        tracer.put_annotation("BookingStatus", "CONFIRMED")

        # Step Functions use the return to append `bookingReference` key into the overall output
        return ret["bookingReference"]
    except BookingConfirmationException as err:
        log_metric(name="FailedBooking", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Status annotation before raising error")
        tracer.put_annotation("BookingStatus", "ERROR")
        logger.error({"operation": "confirm_booking", "details": err})

        raise BookingConfirmationException(details=err)
