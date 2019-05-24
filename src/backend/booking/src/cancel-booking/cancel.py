import json
import os

import boto3
from botocore.exceptions import ClientError


session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(os.environ['BOOKING_TABLE_NAME'])


class BookingCancellationException(Exception):
    pass


def cancel_booking(booking_id):
    try:
        table.update_item(
            Key={'id': booking_id},
            ConditionExpression='id = :idVal',
            UpdateExpression='SET #STATUS = :cancelled',
            ExpressionAttributeNames={'#STATUS': 'status'},
            ExpressionAttributeValues={
                ':idVal': booking_id,
                ':cancelled': 'CANCELLED',
            },
        )

        return {
            'status': 'SUCCESS'
        }
    except ClientError as e:
        raise BookingCancellationException(e.response['Error']['Message'])


def lambda_handler(event, context):

    if 'bookingId' not in event:
        raise BookingCancellationException('Invalid booking ID')

    try:
        ret = cancel_booking(event['bookingId'])
    except BookingCancellationException as e:
        raise BookingCancellationException(e)

    return json.dumps(ret)
