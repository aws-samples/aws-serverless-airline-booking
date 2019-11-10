import json
import os

import boto3
from botocore.exceptions import ClientError

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(os.environ['FLIGHT_TABLE_NAME'])


class FlightReservationException(Exception):
    pass


class FlightFullyBookedException(FlightReservationException):
    pass


class FlightDoesNotExistException(FlightReservationException):
    pass


def reserve_seat_on_flight(flight_id):
    try:
        # TODO: This needs to find the max. In theory, we should never have a situation
        #       where we're trying to increment the seat when one hasn't been
        #       decremented, but just to be sure.
        table.update_item(
            Key={"id": flight_id},
            ConditionExpression="id = :idVal AND seatCapacity < maximumSeating",
            UpdateExpression="SET seatCapacity = seatCapacity + :dec",
            ExpressionAttributeValues={
                ":idVal": flight_id,
                ":dec": 1
            },
        )

        return {
            'status': 'SUCCESS'
        }
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        # Due to no specificity from the DDB error, this could also mean the flight
        # doesn't exist, but we should've caught that earlier in the flow.
        # TODO: Fix that. Could either use TransactGetItems, or Get then Update.
        raise FlightFullyBookedException(f"Flight with ID: {flight_id} is fully booked.")
    except ClientError as e:
        raise FlightReservationException(e.response['Error']['Message'])


def lambda_handler(event, context):
    if 'outboundFlightId' not in event:
        raise ValueError('Invalid arguments')

    try:
        ret = reserve_seat_on_flight(event['outboundFlightId'])
    except FlightReservationException as e:
        raise FlightReservationException(e)

    return json.dumps(ret)
