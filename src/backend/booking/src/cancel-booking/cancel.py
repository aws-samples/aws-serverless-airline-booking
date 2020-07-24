import os

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


class BookingCancellationException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Booking cancellation failed"
        self.details = details or {}


@tracer.capture_method
def cancel_booking(booking_id):
    try:
        logger.debug({"operation": "booking_cancellation", "details": {"booking_id": booking_id}})
        ret = table.update_item(
            Key={"id": booking_id},
            ConditionExpression="id = :idVal",
            UpdateExpression="SET #STATUS = :cancelled",
            ExpressionAttributeNames={"#STATUS": "status"},
            ExpressionAttributeValues={":idVal": booking_id, ":cancelled": "CANCELLED"},
            ReturnValues="UPDATED_NEW",
        )

        logger.info({"operation": "booking_cancellation", "details": ret})
        tracer.put_metadata(booking_id, ret)

        return True
    except ClientError as err:
        logger.exception({"operation": "booking_cancellation"})
        raise BookingCancellationException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@process_booking_handler(logger=logger)
def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to cancel booking

    Parameters
    ----------
    event: dict, required
        Step Functions State Machine event

        chargeId: string
            pre-authorization charge ID

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    -------
    boolean

    Raises
    ------
    BookingCancellationException
        Booking Cancellation Exception including error message upon failure
    """
    booking_id = event.get("bookingId")

    if not booking_id:
        metrics.add_metric(name="InvalidCancellationRequest", unit=MetricUnit.Count, value=1)
        logger.error({"operation": "input_validation", "details": event})
        raise ValueError("Invalid booking ID")

    try:
        logger.debug(f"Cancelling booking - {booking_id}")
        ret = cancel_booking(booking_id)

        metrics.add_metric(name="SuccessfulCancellation", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingStatus", "CANCELLED")

        return ret
    except BookingCancellationException as err:
        metrics.add_metric(name="FailedCancellation", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingStatus", "ERROR")
        logger.exception({"operation": "booking_cancellation"})
        raise
