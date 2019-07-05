import datetime
import json
import os
import uuid

import boto3
from aws_xray_sdk.core import patch, xray_recorder
from botocore.exceptions import ClientError

patched_libs = ('boto3',)
patch(patched_libs)

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(os.environ["BOOKING_TABLE_NAME"])


class BookingReservationException(Exception):
    pass


def is_booking_request_valid(booking):
    return all(
        x in booking
        for x in ["outboundFlightId", "customerId", "chargeId"]
    )


def reserve_booking(booking):
    """Creates a new booking as UNCONFIRMED

    Parameters
    ----------
    booking: dict
        chargeId: string
            pre-authorization charge ID

        stateExecutionId: string
            Step Functions Process Booking Execution ID

        chargeId: string
            Pre-authorization payment token

        customer: string
            Customer unique identifier

        bookingOutboundFlightId: string
            Outbound flight unique identifier

    Returns
    -------
    dict
        bookingId: string
    """
    try:
        with xray_recorder.capture('reserve_booking') as subsegment:
            id = str(uuid.uuid4())

            subsegment.put_annotation("Booking", id)
            subsegment.put_annotation("Customer", booking["customerId"])
            subsegment.put_annotation("Payment", booking["chargeId"])
            subsegment.put_annotation("Flight", booking["outboundFlightId"])

            booking_item = {
                "id": id,
                "stateExecutionId": booking["name"],
                "__typename": "Booking",
                "bookingOutboundFlightId": booking["outboundFlightId"],
                "checkedIn": False,
                "customer": booking["customerId"],
                "paymentToken": booking["chargeId"],
                "status": "UNCONFIRMED",
                "createdAt": str(datetime.datetime.now()),
            }

            table.put_item(Item=booking_item)

            subsegment.put_metadata(id, booking_item, "booking")

        return {"bookingId": id}
    except ClientError as e:
        raise BookingReservationException(e.response["Error"]["Message"])


@xray_recorder.capture('handler')
def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to reserve a booking

    Parameters
    ----------
    event: dict, required
        Step Functions State Machine event

        chargeId: string
            pre-authorization charge ID

        stateExecutionId: string
            Step Functions Process Booking Execution ID

        chargeId: string
            Pre-authorization payment token

        customer: string
            Customer unique identifier

        bookingOutboundFlightId: string
            Outbound flight unique identifier

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    -------
    bookingId: string
        booking ID generated

    Raises
    ------
    BookingReservationException
        Booking Reservation Exception including error message upon failure
    """
    if not is_booking_request_valid(event):
        raise ValueError("Invalid booking request")

    try:
        ret = reserve_booking(event)
    except BookingReservationException as e:
        raise BookingReservationException(e)

    # Step Functions use the return to append `bookingId` key into the overall output
    return ret['bookingId']
