import os

import boto3
from aws_xray_sdk.core import patch, xray_recorder
from botocore.exceptions import ClientError

patched_libs = ('boto3',)
patch(patched_libs)

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(os.environ['BOOKING_TABLE_NAME'])


class BookingCancellationException(Exception):
    pass


def cancel_booking(booking_id):
    try:
        with xray_recorder.capture('cancel_booking') as subsegment:
            subsegment.put_annotation("Booking", booking_id)

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

            subsegment.put_metadata(booking_id, ret, "booking")

        return True
    except ClientError as e:
        raise BookingCancellationException(e.response['Error']['Message'])


@xray_recorder.capture('handler')
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

    try:
        ret = cancel_booking(event['bookingId'])

        return ret
    except BookingCancellationException as e:
        raise BookingCancellationException(e)
