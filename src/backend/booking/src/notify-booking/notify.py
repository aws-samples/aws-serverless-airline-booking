import json
import os

import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from botocore.exceptions import ClientError

patch_all()

session = boto3.Session()
sns = session.client("sns")
booking_sns_topic = os.getenv("BOOKING_TOPIC", "undefined")


class BookingNotificationException(Exception):
    def __init__(self, message="Booking notification failed", status_code=500, details={}):

        super(BookingNotificationException, self).__init__()

        self.message = message
        self.status_code = status_code
        self.details = details


@xray_recorder.capture("## notify_booking")
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

    successful_subject = f"Booking confirmation for {booking_reference}"
    unsuccessful_subject = f"Unable to process booking for {booking_reference}"

    subject = successful_subject if booking_reference else unsuccessful_subject
    booking_status = "confirmed" if booking_reference else "cancelled"

    try:
        ret = sns.publish(
            TopicArn=booking_sns_topic,
            Message=json.dumps(payload),
            Subject=subject,
            MessageAttributes={
                "Booking.Status": {"DataType": "String", "StringValue": booking_status}
            },
        )

        message_id = ret["MessageId"]

        subsegment = xray_recorder.current_subsegment()
        subsegment.put_metadata(booking_reference, ret, "notification")

        return {"notificationId": message_id}
    except ClientError as err:
        raise BookingNotificationException(details=err)


@xray_recorder.capture('## handler')
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
        raise ValueError("Invalid customer and price")

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", event.get("chargeId", "undefined"))
    subsegment.put_annotation("Booking", event.get('bookingId', "undefined"))
    subsegment.put_annotation("Customer", event.get('customerId', "undefined"))
    subsegment.put_annotation("Flight", event.get('outboundFlightId', "undefined"))
    subsegment.put_annotation("BookingReference", booking_reference)

    try:
        payload = {"customerId": customer_id, "price": price}
        ret = notify_booking(payload, booking_reference)
        subsegment.put_annotation("BookingNotification", ret['notificationId'])

        # Step Functions use the return to append `notificationId` key into the overall output
        return ret["notificationId"]
    except BookingNotificationException as err:
        subsegment.put_metadata("notify_booking_error", err, "booking")
        raise BookingNotificationException(details=err)
