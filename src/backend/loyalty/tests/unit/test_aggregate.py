from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_mock import MockerFixture

from loyalty.aggregate import app
from loyalty.shared.storage import FakeStorage
from tests.utils import make_loyalty_points


def test_aggregate_loyalty_points():
    # GIVEN
    storage = FakeStorage()
    loyalty_points = make_loyalty_points(count=3)

    # WHEN
    aggregated = app.aggregate_loyalty_points(records=loyalty_points, storage_client=storage)

    # THEN
    assert len(aggregated) == 1
    assert len(storage.aggregates) == 1


def test_aggregate_lambda_handler(mocker: MockerFixture, dynamodb_stream_records: dict, lambda_context: LambdaContext):
    # GIVEN
    storage = FakeStorage()

    # WHEN
    mocker.patch.object(app.DynamoDBStorage, "from_env", return_value=storage)
    app.lambda_handler(event=dynamodb_stream_records, context=lambda_context)

    # THEN
    assert len(storage.aggregates) == 3  # down from 6 stream records
