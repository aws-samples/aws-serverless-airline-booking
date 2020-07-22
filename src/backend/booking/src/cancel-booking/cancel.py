import os

import boto3
from botocore.exceptions import ClientError

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit

# TODO: Migrate original Powertools to newly OSS Powertools as a custom middleware
from lambda_python_powertools.logging import logger_inject_process_booking_sfn, logger_setup
from lambda_python_powertools.tracing import Tracer

logger = logger_setup()
tracer = Tracer()
metrics = Metrics()

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table_name = os.getenv("BOOKING_TABLE_NAME", "undefined")
table = dynamodb.Table(table_name)


class BookingCancellationException(Exception):
    def __init__(self, message=None, status_code=None, details=None):

        super(BookingCancellationException, self).__init__()

        self.message = message or "Booking cancellation failed"
        self.status_code = status_code or 500
        self.details = details or {}


@tracer.capture_method
def cancel_booking(booking_id):
    try:
        logger.debug({"operation": "cancel_booking", "details": {"booking_id": booking_id}})
        ret = table.update_item(
            Key={"id": booking_id},
            ConditionExpression="id = :idVal",
            UpdateExpression="SET #STATUS = :cancelled",
            ExpressionAttributeNames={"#STATUS": "status"},
            ExpressionAttributeValues={":idVal": booking_id, ":cancelled": "CANCELLED"},
            ReturnValues="UPDATED_NEW",
        )

        logger.info({"operation": "cancel_booking", "details": ret})
        logger.debug("Adding update item operation result as tracing metadata")
        tracer.put_metadata(booking_id, ret)

        return True
    except ClientError as err:
        logger.debug({"operation": "cancel_booking", "details": err})
        raise BookingCancellationException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@tracer.capture_lambda_handler(process_booking_sfn=True)
@logger_inject_process_booking_sfn
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
        logger.error({"operation": "invalid_event", "details": event})
        raise ValueError("Invalid booking ID")

    try:
        logger.debug(f"Cancelling booking - {booking_id}")
        ret = cancel_booking(booking_id)

        metrics.add_metric(name="SuccessfulCancellation", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Status annotation")
        tracer.put_annotation("BookingStatus", "CANCELLED")

        return ret
    except BookingCancellationException as err:
        metrics.add_metric(name="FailedCancellation", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Status annotation before raising error")
        tracer.put_annotation("BookingStatus", "ERROR")
        logger.error({"operation": "cancel_booking", "details": err})

        raise BookingCancellationException(details=err)
