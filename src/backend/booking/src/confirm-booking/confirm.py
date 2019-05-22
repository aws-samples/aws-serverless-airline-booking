import json
import os

import boto3
from botocore.exceptions import ClientError

import shortuuid

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(os.environ["BOOKING_TABLE_NAME"])


class BookingConfirmationException(Exception):
    pass


def confirm_booking(booking_id):
    try:
        reference = shortuuid.ShortUUID().random(length=6)
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

    if "bookingId" not in event:
        raise BookingConfirmationException("Invalid booking ID")

    try:
        ret = confirm_booking(event["bookingId"])
    except BookingConfirmationException as e:
        raise BookingConfirmationException(e)

    return json.dumps(ret)
