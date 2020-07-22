import json
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
sns = session.client("sns")
booking_sns_topic = os.getenv("BOOKING_TOPIC", "undefined")


class BookingNotificationException(Exception):
    def __init__(self, message=None, status_code=None, details=None):

        super(BookingNotificationException, self).__init__()

        self.message = message or "Booking notification failed"
        self.status_code = status_code or 500
        self.details = details or {}


@tracer.capture_method
def notify_booking(payload, booking_reference):
    """Notify whether a booking have been processed successfully

    Parameters
    ----------
    payload: dict
        Payload to be sent as notification

        customerId: string
            Unique Customer ID

        price: string
            Flight price

    booking_reference: string
        Confirmed booking reference

    Returns
    -------
    dict
        notificationId: string
            Unique ID confirming notification delivery

    Raises
    ------
    BookingNotificationException
        Booking Notification Exception including error message upon failure
    """

    booking_reference = booking_reference or "most recent booking"
    successful_subject = f"Booking confirmation for {booking_reference}"
    unsuccessful_subject = f"Unable to process booking for {booking_reference}"

    subject = successful_subject if booking_reference else unsuccessful_subject
    booking_status = "confirmed" if booking_reference else "cancelled"

    try:
        logger.debug(
            {
                "operation": "notify_booking",
                "details": {
                    "customer_id": payload["customerId"],
                    "booking_price": payload["price"],
                    "booking_status": booking_status,
                },
            }
        )
        ret = sns.publish(
            TopicArn=booking_sns_topic,
            Message=json.dumps(payload),
            Subject=subject,
            MessageAttributes={
                "Booking.Status": {"DataType": "String", "StringValue": booking_status}
            },
        )

        logger.info({"operation": "notify_booking", "details": ret})
        logger.debug("Adding publish notification operation result as tracing metadata")
        tracer.put_metadata(booking_reference, ret)

        return {"notificationId": ret["MessageId"]}
    except ClientError as err:
        logger.debug({"operation": "notify_booking", "details": err})
        raise BookingNotificationException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@tracer.capture_lambda_handler(process_booking_sfn=True)
@logger_inject_process_booking_sfn
def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to notify booking

    Parameters
    ----------
    event: dict, required
        Step Functions State Machine event

        customer_id: string
            Unique Customer ID

        price: string
            Flight price

        bookingReference: string
            Confirmed booking reference

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    -------
    string
        notificationId
            Unique ID confirming notification delivery

    Raises
    ------
    BookingNotificationException
        Booking Notification Exception including error message upon failure
    """
    customer_id = event.get("customerId", False)
    payment = event.get("payment", {})
    price = payment.get("price", False)
    booking_reference = event.get("bookingReference", False)

    if not customer_id and not price:
        metrics.add_metric(name="InvalidNotificationRequest", unit=MetricUnit.Count, value=1)
        logger.error({"operation": "invalid_event", "details": event})
        raise ValueError("Invalid customer and price")

    try:
        payload = {"customerId": customer_id, "price": price}
        ret = notify_booking(payload, booking_reference)

        metrics.add_metric(name="SuccessfulNotification", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Notification annotation")
        tracer.put_annotation("BookingNotification", ret["notificationId"])
        tracer.put_annotation("BookingNotificationStatus", "SUCCESS")

        # Step Functions use the return to append `notificationId` key into the overall output
        return ret["notificationId"]
    except BookingNotificationException as err:
        metrics.add_metric(name="FailedNotification", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Booking Notification annotation before raising error")
        tracer.put_annotation("BookingNotificationStatus", "FAILED")
        logger.error({"operation": "notify_booking", "details": err})
        raise BookingNotificationException(details=err)
