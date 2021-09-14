import pytest
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent
from botocore.exceptions import ClientError
from botocore.stub import ANY, Stubber
from loyalty.shared.functions import calculate_aggregate_points
from loyalty.shared.models import LoyaltyPoint, LoyaltyPointAggregateDynamoDB, LoyaltyTier
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


def test_get_loyalty_points(dynamodb_storage: DynamoDBStorage, transaction: LoyaltyPoint):
    # GIVEN
    get_item_params = {
        "Key": {"pk": f"CUSTOMER#{transaction.customerId}", "sk": "AGGREGATE"},
        "AttributesToGet": ["totalPoints", "tier"],
        "TableName": "test",
    }
    with Stubber(dynamodb_storage.client.meta.client) as stub:
        stub.add_response("get_item", {"Item": {"tier": {"S": "BRONZE"}, "totalPoints": {"N": "100"}}}, get_item_params)

        tier, points = dynamodb_storage.get_customer_tier_points(customer_id=transaction.customerId)  # WHEN
        # THEN
        stub.assert_no_pending_responses()
        assert tier == LoyaltyTier.BRONZE
        assert points == 100


def test_add_loyalty_points(dynamodb_storage: DynamoDBStorage, transaction):
    # GIVEN
    put_item_params = {
        "Item": {
            **dynamodb_storage.build_add_transaction_item(item=transaction),
            "sk": ANY,
            "createdAt": ANY,
        },
        "TableName": "test",
    }

    with Stubber(dynamodb_storage.client.meta.client) as stub:
        stub.add_response("put_item", {}, put_item_params)
        dynamodb_storage.add(item=transaction)  # WHEN
        stub.assert_no_pending_responses()  # THEN


def test_aggregate_loyalty_points(dynamodb_storage: DynamoDBStorage, aggregate_records):
    # GIVEN
    loyalty_aggregates = DynamoDBStorage.build_loyalty_point_aggregate(event=DynamoDBStreamEvent(aggregate_records))
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)
    loyalty_update_items = DynamoDBStorage.build_add_aggregate_transaction_item(customers=aggregated_customers)

    with Stubber(dynamodb_storage.client.meta.client) as stub:
        for item in loyalty_update_items:
            expected_param = expected_params_update_item_aggregate(data=item)
            stub.add_response("update_item", {}, expected_param)

        dynamodb_storage.add_aggregate(items=aggregated_customers)  # WHEN
        stub.assert_no_pending_responses()  # THEN


def test_aggregate_loyalty_points_ignore_modify(dynamodb_storage: DynamoDBStorage, aggregate_modify_records):
    # GIVEN
    loyalty_aggregates = dynamodb_storage.build_loyalty_point_aggregate(
        event=DynamoDBStreamEvent(aggregate_modify_records)
    )
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)

    with Stubber(dynamodb_storage.client.meta.client) as stub:
        dynamodb_storage.add_aggregate(items=aggregated_customers)  # WHEN
        stub.assert_no_pending_responses()  # THEN


def test_client_errors_propagate(dynamodb_storage: DynamoDBStorage, aggregate_records, transaction: LoyaltyPoint):
    loyalty_aggregates = DynamoDBStorage.build_loyalty_point_aggregate(event=DynamoDBStreamEvent(aggregate_records))
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)

    with pytest.raises(ClientError, match="ResourceNotFoundException"):
        dynamodb_storage.add_aggregate(items=aggregated_customers)
        dynamodb_storage.add(item=transaction)
        dynamodb_storage.get_customer_tier_points(customer_id=transaction.customerId)
