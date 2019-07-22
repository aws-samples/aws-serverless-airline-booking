import datetime
import json
import os
import uuid

import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from botocore.exceptions import ClientError

patch_all()

session = boto3.Session()
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(os.getenv("BOOKING_TABLE_NAME", "undefined"))


class BookingReservationException(Exception):
    def __init__(
        self, message="Booking reservation failed", status_code=500, details={}
    ):

        super(BookingReservationException, self).__init__()

        self.message = message
        self.status_code = status_code
        self.details = details


def is_booking_request_valid(booking):
    return all(x in booking for x in ["outboundFlightId", "customerId", "chargeId"])


@xray_recorder.capture("## reserve_booking")
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
        id = str(uuid.uuid4())

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

        subsegment = xray_recorder.current_subsegment()
        subsegment.put_metadata(id, booking_item, "booking")

        return {"bookingId": id}
    except ClientError as err:
        raise BookingReservationException(details=err)


@xray_recorder.capture("## handler")
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

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", event.get("chargeId", "undefined"))
    subsegment.put_annotation("Customer", event.get("customerId", "undefined"))
    subsegment.put_annotation("Flight", event.get("outboundFlightId", "undefined"))

    try:
        ret = reserve_booking(event)
        subsegment.put_annotation("Booking", ret["bookingId"])
        subsegment.put_annotation("BookingStatus", "RESERVED")

        # Step Functions use the return to append `bookingId` key into the overall output
        return ret["bookingId"]
    except BookingReservationException as err:
        subsegment.put_annotation("BookingStatus", "ERROR")
        subsegment.put_metadata("reserve_booking_error", err, "booking")
        raise BookingReservationException(details=err)
