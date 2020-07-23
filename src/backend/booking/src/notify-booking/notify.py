import json
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
sns = session.client("sns")
booking_sns_topic = os.getenv("BOOKING_TOPIC", "undefined")


class BookingNotificationException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Booking notification failed"
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
                "operation": "booking_notification",
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

        logger.info({"operation": "booking_notification", "details": ret})
        tracer.put_metadata(booking_reference, ret)

        return {"notificationId": ret["MessageId"]}
    except ClientError as err:
        logger.debug({"operation": "booking_notification"})
        raise BookingNotificationException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@process_booking_handler(logger=logger)
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
        logger.error({"operation": "input_validation", "details": event})
        raise ValueError("Invalid customer and price")

    try:
        payload = {"customerId": customer_id, "price": price}
        ret = notify_booking(payload, booking_reference)

        metrics.add_metric(name="SuccessfulNotification", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingNotification", ret["notificationId"])
        tracer.put_annotation("BookingNotificationStatus", "SUCCESS")

        # Step Functions use the return to append `notificationId` key into the overall output
        return ret["notificationId"]
    except BookingNotificationException as err:
        metrics.add_metric(name="FailedNotification", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("BookingNotificationStatus", "FAILED")
        logger.exception({"operation": "booking_notification"})
        raise
