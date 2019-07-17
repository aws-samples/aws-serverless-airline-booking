import os

import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from botocore.exceptions import ClientError

patch_all()

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(os.getenv('BOOKING_TABLE_NAME', "undefined"))


class BookingCancellationException(Exception):
    def __init__(self, message="Booking cancellation failed", status_code=500, details={}):

        super(BookingCancellationException, self).__init__()

        self.message = message
        self.status_code = status_code
        self.details = details


@xray_recorder.capture('## cancel_booking')
def cancel_booking(booking_id):
    try:
        ret = table.update_item(
            Key={'id': booking_id},
            ConditionExpression='id = :idVal',
            UpdateExpression='SET #STATUS = :cancelled',
            ExpressionAttributeNames={'#STATUS': 'status'},
            ExpressionAttributeValues={
                ':idVal': booking_id,
                ':cancelled': 'CANCELLED',
            },
            ReturnValues="UPDATED_NEW",
        )

        subsegment = xray_recorder.current_subsegment()
        subsegment.put_metadata(booking_id, ret, "booking")

        return True
    except ClientError as err:
        raise BookingCancellationException(details=err)


@xray_recorder.capture('## handler')
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
    if 'bookingId' not in event:
        raise ValueError('Invalid booking ID')

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", event.get("chargeId", "undefined"))
    subsegment.put_annotation("Booking", event.get('bookingId', "undefined"))
    subsegment.put_annotation("Customer", event.get('customerId', "undefined"))
    subsegment.put_annotation("Flight", event.get('outboundFlightId', "undefined"))
    subsegment.put_annotation("StateMachineExecution", event.get('name', "undefined"))

    try:
        ret = cancel_booking(event['bookingId'])
        subsegment.put_annotation("BookingStatus", "CANCELLED")

        return ret
    except BookingCancellationException as err:
        subsegment.put_annotation("BookingStatus", "ERROR")
        subsegment.put_metadata("cancel_booking_error", err, "booking")
        raise BookingCancellationException(details=err)
