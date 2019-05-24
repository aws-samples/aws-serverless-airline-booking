import json
import os
import datetime

import boto3
from botocore.exceptions import ClientError
import uuid

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(os.environ['BOOKING_TABLE_NAME'])


class BookingReservationException(Exception):
    pass

def is_booking_request_valid(booking):
    return True

def reserve_booking(booking):
    try:
        id = str(uuid.uuid4())
        table.put_item(
            Item={
                'id': id, 
                'stateExecutionId': booking['stateExecutionId'],
                '__typename': 'Booking',
                'bookingOutboundFlightId': booking['bookingOutboundFlightId'],
                'checkedIn': False,
                'customer': booking['customer'],
                'paymentToken': booking['chargeId'],
                'status': 'UNCONFIRMED',
                'createdAt': str(datetime.datetime.now())
            }
        )

        return {
            'bookingId': id
        }
    except ClientError as e:
        raise BookingReservationException(e.response['Error']['Message'])
        

def lambda_handler(event, context):

    if not is_booking_request_valid(event):
        raise BookingReservationException('Invalid booking request')

    try:
        ret = reserve_booking(event)
    except BookingReservationException as e:
        raise BookingReservationException(e)

    return json.dumps(ret)

