import json
import os
import random
import string

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

error_string = '{{ "Status" : "Failed", "Error" : "{}" }}'

def generate_booking_reference(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb", region_name='eu-west-2')
    table = dynamodb.Table(os.environ['BOOKING_TABLE_NAME'])
    return_val = error_string.format('Unknown error.')

    # Validate the input
    try:
        booking_id = event['bookingId']
    except:
        raise BookingConfirmationException("No booking_id provided.")
    try:
        # Just take the first one and write the redeemer to it.
        reference = generate_booking_reference(6)
        update_response = table.update_item(
            Key={
                'id': booking_id
            },
            ConditionExpression= 'id = :idVal',
            UpdateExpression='set bookingReference = :br',
            ExpressionAttributeValues={
                ':br': reference,
                ':idVal': booking_id
            }
        )
        return_val = '{{ "Status" : "Success", "BookingReference" : "{}" }}'.format(reference)
    except ClientError as e:
        raise BookingConfirmationException(e.response['Error']['Message'])
    return json.loads(return_val)
    
class BookingConfirmationException(Exception):
    pass
