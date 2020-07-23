import os
import secrets

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


class BookingConfirmationException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Booking confirmation failed"
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
        reference = secrets.token_urlsafe(4)
        logger.debug(
            {
                "operation": "booking_confirmation",
                "details": {"booking_id": booking_id, "booking_reference": reference},
            }
        )
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

        logger.info({"operation": "booking_confirmation", "details": ret})
        tracer.put_metadata(booking_id, ret)

        return {"bookingReference": reference}
    except ClientError as err:
        logger.exception({"operation": "booking_confirmation"})
        raise BookingConfirmationException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@process_booking_handler(logger=logger)
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
    booking_id = event.get("bookingId")
    if not booking_id:
        metrics.add_metric(name="InvalidConfirmationRequest", unit=MetricUnit.Count, value=1)
        logger.error({"operation": "input_validation", "details": event})
        raise ValueError("Invalid booking ID")

    try:
        logger.debug(f"Confirming booking - {booking_id}")
        ret = confirm_booking(booking_id)

        metrics.add_metric(name="SuccessfulBooking", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingReference", ret["bookingReference"])
        tracer.put_annotation("BookingStatus", "CONFIRMED")

        # Step Functions use the return to append `bookingReference` key into the overall output
        return ret["bookingReference"]
    except BookingConfirmationException as err:
        metrics.add_metric(name="FailedBooking", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingStatus", "ERROR")
        logger.exception({"operation": "booking_confirmation"})
        raise
