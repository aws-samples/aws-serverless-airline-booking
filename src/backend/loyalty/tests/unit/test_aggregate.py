from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import DynamoDBStreamEvent
from loyalty.aggregate import app
from loyalty.shared.storage import DynamoDBStorage, FakeStorage


def test_handler_process_ddb_stream_insert_remove(mocker, aggregate_records, lambda_context):
    storage = FakeStorage()
    app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=storage)
    app.lambda_handler(event=aggregate_records, context=lambda_context)


def test_aggregate_loyalty_points(aggregate_records):
    st = FakeStorage()
    records = DynamoDBStorage.build_loyalty_point_list(event=DynamoDBStreamEvent(aggregate_records))
    aggregated = app.aggregate_loyalty_points(records=records, storage_client=st)
    assert len(records) == 6
    assert len(aggregated) == 3
