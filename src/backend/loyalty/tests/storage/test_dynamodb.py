import pytest
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent
from botocore.exceptions import ClientError
from botocore.stub import ANY, Stubber
from loyalty.shared.functions import calculate_aggregate_points
from loyalty.shared.models import LoyaltyPoint, LoyaltyTier
from loyalty.shared.storage import DynamoDBStorage

# NOTE: Pytest has


def test_get_loyalty_points(dynamodb_storage: DynamoDBStorage, transaction: LoyaltyPoint):
    # GIVEN
    get_item_params = dynamodb_storage.build_get_loyalty_tier_points_get_item_input(customer_id=transaction.customerId)
    get_item_params["TableName"] = "test"
    with Stubber(dynamodb_storage.client.meta.client) as stub:
        stub.add_response("get_item", {"Item": {"tier": {"S": "BRONZE"}, "totalPoints": {"N": "100"}}}, get_item_params)

        tier, points = dynamodb_storage.get_customer_tier_points(customer_id=transaction.customerId)  # WHEN
        # THEN
        stub.assert_no_pending_responses()
        assert tier == LoyaltyTier.BRONZE
        assert points == 100


def test_add_loyalty_points(dynamodb_storage: DynamoDBStorage, transaction):
    # GIVEN
    put_item_params = dynamodb_storage.build_add_put_item_input(item=transaction)
    put_item_params["TableName"] = "test"
    put_item_params["Item"]["sk"] = ANY
    put_item_params["Item"]["createdAt"] = ANY
    with Stubber(dynamodb_storage.client.meta.client) as stub:
        stub.add_response("put_item", {}, put_item_params)
        dynamodb_storage.add(item=transaction)  # WHEN
        stub.assert_no_pending_responses()  # THEN


def test_aggregate_loyalty_points(dynamodb_storage: DynamoDBStorage, aggregate_records):
    # GIVEN
    loyalty_aggregates = DynamoDBStorage.build_loyalty_point_list(event=DynamoDBStreamEvent(aggregate_records))
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)
    update_item_inputs = DynamoDBStorage.build_add_aggregate_update_item_input(customers=aggregated_customers)

    with Stubber(dynamodb_storage.client.meta.client) as stub:
        for transaction in update_item_inputs:
            transaction["ExpressionAttributeValues"][":timestamp"] = ANY  # type: ignore
            transaction["TableName"] = "test"
            stub.add_response("update_item", {}, transaction)

        dynamodb_storage.add_aggregate(items=aggregated_customers)  # WHEN
        stub.assert_no_pending_responses()  # THEN


def test_aggregate_loyalty_points_ignore_modify(dynamodb_storage: DynamoDBStorage, aggregate_modify_records):
    # GIVEN
    loyalty_aggregates = DynamoDBStorage.build_loyalty_point_list(event=DynamoDBStreamEvent(aggregate_modify_records))
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)

    with Stubber(dynamodb_storage.client.meta.client) as stub:
        dynamodb_storage.add_aggregate(items=aggregated_customers)  # WHEN
        stub.assert_no_pending_responses()  # THEN


def test_client_errors_propagate(dynamodb_storage: DynamoDBStorage, aggregate_records, transaction: LoyaltyPoint):
    loyalty_aggregates = DynamoDBStorage.build_loyalty_point_list(event=DynamoDBStreamEvent(aggregate_records))
    aggregated_customers = calculate_aggregate_points(records=loyalty_aggregates)

    with pytest.raises(ClientError, match="ResourceNotFoundException"):
        dynamodb_storage.add_aggregate(items=aggregated_customers)

    with pytest.raises(ClientError, match="ResourceNotFoundException"):
        dynamodb_storage.add(item=transaction)

    with pytest.raises(ClientError, match="ResourceNotFoundException"):
        dynamodb_storage.get_customer_tier_points(customer_id=transaction.customerId)
