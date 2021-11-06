from typing import List

from loyalty.aggregate import app
from loyalty.shared.models import LoyaltyPoint
from loyalty.shared.storage import FakeStorage


def test_handler_process_ddb_stream_insert_remove(mocker, aggregate_records, lambda_context):
    storage = FakeStorage()
    app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=storage)
    app.lambda_handler(event=aggregate_records, context=lambda_context)


def test_aggregate_loyalty_points(fake_loyalty_points: List[LoyaltyPoint]):
    st = FakeStorage()
    aggregated = app.aggregate_loyalty_points(records=fake_loyalty_points, storage_client=st)
    assert len(fake_loyalty_points) == 2
    assert len(aggregated) == 1
