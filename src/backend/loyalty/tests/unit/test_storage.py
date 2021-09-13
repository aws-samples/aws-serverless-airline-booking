from typing import Tuple
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent
from botocore.stub import ANY, Stubber
from mypy_boto3_dynamodb import ServiceResource
from loyalty import aggregate, get, ingest
from loyalty.shared.functions import calculate_aggregate_points
from loyalty.shared.models import LoyaltyPoint, LoyaltyPointAggregateDynamoDB
from loyalty.shared.storage import DynamoDBStorage


def expected_params_update_item_aggregate(data: LoyaltyPointAggregateDynamoDB):
    return {
        "ConditionExpression": "not(contains(bookings, :booking))",
        "ExpressionAttributeValues": {
            ":booking": data["bookingId"],
            ":bookings": {data["bookingId"]},
            ":incr": data["total_points"],
            ":tier": data["tier"],
            ":timestamp": ANY,
        },
        "Key": {"pk": data["pk"], "sk": data["sk"]},
        "TableName": "test",
        "UpdateExpression": "ADD totalPoints :incr, bookings :bookings SET tier = :tier, updatedAt = :timestamp",
    }


def test_get_loyalty_points(dynamodb_stub: Tuple[DynamoDBStorage, Stubber], transaction: LoyaltyPoint):
    # GIVEN
    get_item_params = {
        "Key": {"pk": f"CUSTOMER#{transaction.customerId}", "sk": "AGGREGATE"},
        "AttributesToGet": ["totalPoints", "tier"],
        "TableName": "test",
    }
    # WHEN
    ddb_storage, stubber = dynamodb_stub
    stubber.add_response("get_item", {"Item": {"tier": {"S": "BRONZE"}}}, get_item_params)
    # THEN
    ddb_storage.get_customer_tier_points(customer_id=transaction.customerId)


def test_add_loyalty_points(dynamodb_stub: Tuple[DynamoDBStorage, Stubber], transaction):
    # GIVEN
    put_item_params = {
        "Item": {
            **DynamoDBStorage.build_add_transaction_item(item=transaction),
            "sk": ANY,
            "createdAt": ANY,
        },
        "TableName": "test",
    }
    # WHEN
    ddb_storage, stubber = dynamodb_stub
    stubber.add_response("put_item", {}, put_item_params)
    # THEN
    ddb_storage.add(item=transaction)


def test_aggregate_loyalty_points(dynamodb_stub: Tuple[DynamoDBStorage, Stubber], aggregate_records):
    # GIVEN
    loyalty_aggregates = DynamoDBStorage.build_loyalty_point_aggregate(event=DynamoDBStreamEvent(aggregate_records))
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)
    loyalty_update_items = DynamoDBStorage.build_add_aggregate_transaction_item(customers=aggregated_customers)

    # WHEN
    ddb_storage, stubber = dynamodb_stub
    for item in loyalty_update_items:
        expected_param = expected_params_update_item_aggregate(data=item)
        stubber.add_response("update_item", {}, expected_param)

    # THEN
    ddb_storage.add_aggregate(items=aggregated_customers)
