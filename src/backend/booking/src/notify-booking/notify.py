import json
import os

import boto3
from botocore.exceptions import ClientError

session = boto3.Session()
sns = session.client("sns")
booking_sns_topic = os.getenv("BOOKING_TOPIC")


class BookingNotificationException(Exception):
    pass


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

        return {"notificationId": ret["MessageId"]}
    except ClientError as e:
        raise BookingNotificationException(e.response["Error"]["Message"])


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
    price = event.get("payment", False).get("price", False)  # ['payment']['price'] w/ defaults if either is empty/undefined

    booking_reference = event.get("bookingReference", False)

    if not customer_id and not price:
        raise ValueError("Invalid customer and price")

    try:
        payload = {"customerId": customer_id, "price": price}
        ret = notify_booking(payload, booking_reference)
    except BookingNotificationException as e:
        raise BookingNotificationException(e)

    # Step Functions use the return to append `notificationId` key into the overall output
    return ret["notificationId"]
