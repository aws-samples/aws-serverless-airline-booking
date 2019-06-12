import json
import os
import secrets

import boto3
from botocore.exceptions import ClientError

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(os.environ["BOOKING_TABLE_NAME"])


class BookingConfirmationException(Exception):
    pass


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
        table.update_item(
            Key={"id": booking_id},
            ConditionExpression="id = :idVal",
            UpdateExpression="SET bookingReference = :br, #STATUS = :confirmed",
            ExpressionAttributeNames={"#STATUS": "status"},
            ExpressionAttributeValues={
                ":br": reference,
                ":idVal": booking_id,
                ":confirmed": "CONFIRMED",
            },
        )

        return {
            "bookingReference": reference
        }
    except ClientError as e:
        raise BookingConfirmationException(e.response["Error"]["Message"])


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

    try:
        ret = confirm_booking(event["bookingId"])
    except BookingConfirmationException as e:
        raise BookingConfirmationException(e)

    # Step Functions use the return to append `bookingReference` key into the overall output
    return ret['bookingReference']
