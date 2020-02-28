import os


import boto3
from botocore.exceptions import ClientError

from lambda_python_powertools.logging import (
    logger_inject_process_booking_sfn,
    logger_setup,
    MetricUnit,
    log_metric,
)
from lambda_python_powertools.tracing import Tracer

logger = logger_setup()
tracer = Tracer()

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table_name = os.getenv("BOOKING_TABLE_NAME", "undefined")
table = dynamodb.Table(table_name)

_cold_start = True


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
    global _cold_start
    if _cold_start:
        log_metric(
            name="ColdStart", unit=MetricUnit.Count, value=1, function_name=context.function_name
        )
        _cold_start = False

    booking_id = event.get("bookingId")

    if not booking_id:
        log_metric(
            name="InvalidBookingRequest", unit=MetricUnit.Count, value=1, operation="cancel_booking"
        )
        logger.error({"operation": "invalid_event", "details": event})
        raise ValueError("Invalid booking ID")

    try:
        logger.debug(f"Cancelling booking - {booking_id}")
        ret = cancel_booking(booking_id)

        log_metric(name="SuccessfulCancellation", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Status annotation")
        tracer.put_annotation("BookingStatus", "CANCELLED")

        return ret
    except BookingCancellationException as err:
        log_metric(name="FailedCancellation", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Status annotation before raising error")
        tracer.put_annotation("BookingStatus", "ERROR")
        logger.error({"operation": "cancel_booking", "details": err})

        raise BookingCancellationException(details=err)
