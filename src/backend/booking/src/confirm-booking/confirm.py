import json
import os
import secrets

import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from botocore.exceptions import ClientError

patch_all()

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(os.getenv("BOOKING_TABLE_NAME", "undefined"))


class BookingConfirmationException(Exception):
    def __init__(
        self, message="Booking confirmation failed", status_code=500, details={}
    ):

        super(BookingConfirmationException, self).__init__()

        self.message = message
        self.status_code = status_code
        self.details = details


@xray_recorder.capture("## confirm_booking")
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

        subsegment = xray_recorder.current_subsegment()
        subsegment.put_metadata(booking_id, ret, "booking")

        return {"bookingReference": reference}
    except ClientError as err:
        raise BookingConfirmationException(details=err)


@xray_recorder.capture("## handler")
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

    if "bookingId" not in event:
        raise ValueError("Invalid booking ID")

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", event.get("chargeId", "undefined"))
    subsegment.put_annotation("Booking", event.get("bookingId", "undefined"))
    subsegment.put_annotation("Customer", event.get("customerId", "undefined"))
    subsegment.put_annotation("Flight", event.get("outboundFlightId", "undefined"))
    subsegment.put_annotation("StateMachineExecution", event.get("name", "undefined"))

    try:
        ret = confirm_booking(event["bookingId"])
        subsegment.put_annotation("BookingReference", ret["bookingReference"])
        subsegment.put_annotation("BookingStatus", "CONFIRMED")

        # Step Functions use the return to append `bookingReference` key into the overall output
        return ret["bookingReference"]
    except BookingConfirmationException as err:
        subsegment.put_annotation("BookingStatus", "ERROR")
        subsegment.put_metadata("confirm_booking_error", err, "booking")
        raise BookingConfirmationException(details=err)
