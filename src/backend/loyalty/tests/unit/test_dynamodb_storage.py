from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent
from botocore.stub import ANY, Stubber
from mypy_boto3_dynamodb.type_defs import GetItemInputRequestTypeDef, PutItemInputRequestTypeDef

from loyalty.shared.functions import calculate_aggregate_points
from loyalty.shared.models import LoyaltyTier
from tests.utils import make_dynamodb_storage, make_loyalty_point, make_loyalty_points


def test_get_loyalty_points():
    # GIVEN
    storage = make_dynamodb_storage()
    loyalty_points = make_loyalty_point()
    get_item_key_attrs = storage.build_get_loyalty_tier_points_get_item_input(customer_id=loyalty_points.customerId)
    get_item_request: GetItemInputRequestTypeDef = {"TableName": "test", **get_item_key_attrs}  # type: ignore
    get_item_response = {"Item": {"tier": {"S": "BRONZE"}, "totalPoints": {"N": "100"}}}

    # WHEN
    with Stubber(storage.client.meta.client) as stub:
        stub.add_response("get_item", get_item_response, get_item_request)
        tier, points = storage.get_customer_tier_points(customer_id=loyalty_points.customerId)

    # THEN
    stub.assert_no_pending_responses()
    assert tier == LoyaltyTier.BRONZE
    assert points == 100


def test_add_loyalty_points():
    # GIVEN
    storage = make_dynamodb_storage()
    loyalty_points = make_loyalty_point()
    put_item_key_attrs = storage.build_add_put_item_input(item=loyalty_points)
    put_item_key_attrs["Item"].update(sk=ANY)
    put_item_request: PutItemInputRequestTypeDef = {"TableName": "test", **put_item_key_attrs}  # type: ignore
    put_item_response = {}

    # WHEN
    with Stubber(storage.client.meta.client) as stub:
        stub.add_response("put_item", put_item_response, put_item_request)
        storage.add(item=loyalty_points)

    # THEN
    stub.assert_no_pending_responses()


def test_aggregate_loyalty_points():
    # GIVEN
    storage = make_dynamodb_storage()
    loyalty_transactions = make_loyalty_points()
    loyalty_transactions_aggregated = calculate_aggregate_points(records=loyalty_transactions)
    update_item_requests = storage.build_add_aggregate_update_item_input(customers=loyalty_transactions_aggregated)
    update_item_response = {}  # type: ignore

    # WHEN
    with Stubber(storage.client.meta.client) as stub:
        for update_item_request in update_item_requests:
            update_item_request["TableName"] = "test"
            stub.add_response("update_item", update_item_response, update_item_request)

        storage.add_aggregate(items=loyalty_transactions_aggregated)

    # THEN
    stub.assert_no_pending_responses()


def test_aggregate_loyalty_points_ignore_modify_events(dynamodb_stream_modify_records: DynamoDBStreamEvent):
    # GIVEN
    storage = make_dynamodb_storage()
    loyalty_transactions = storage.build_loyalty_point_list(event=dynamodb_stream_modify_records)
    loyalty_transactions_aggregated = calculate_aggregate_points(records=loyalty_transactions)

    # WHEN
    storage.add_aggregate(items=loyalty_transactions_aggregated)

    # THEN
    assert loyalty_transactions == []
    assert loyalty_transactions_aggregated == {}


def test_aggregate_loyalty_points_ignore_aggregate_events(dynamodb_stream_aggregate_records: DynamoDBStreamEvent):
    # GIVEN
    storage = make_dynamodb_storage()
    loyalty_transactions = storage.build_loyalty_point_list(event=dynamodb_stream_aggregate_records)
    loyalty_transactions_aggregated = calculate_aggregate_points(records=loyalty_transactions)

    # WHEN
    storage.add_aggregate(items=loyalty_transactions_aggregated)
    # THEN
    assert loyalty_transactions == []
    assert loyalty_transactions_aggregated == {}
