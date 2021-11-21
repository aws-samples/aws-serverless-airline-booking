import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_mock import MockerFixture

from loyalty.ingest import app
from loyalty.shared.storage import FakeStorage
from tests.utils import make_loyalty_point


def test_ingest_loyalty_points():
    # GIVEN
    storage = FakeStorage()
    loyalty_point = make_loyalty_point()

    # WHEN
    app.ingest_loyalty_points(transaction=loyalty_point, storage_client=storage)

    # THEN
    assert loyalty_point in storage


def test_ingest_invalid_record(record):
    # GIVEN
    record["body"] = '{"customerId":"1234","price":100}'  # v1 payload
    with pytest.raises(ValueError, match="Invalid payload"):
        app.sqs_record_handler(record=record)


def test_ingest_lambda_handler(mocker: MockerFixture, sqs_records: dict, lambda_context: LambdaContext):
    # GIVEN
    storage = FakeStorage()
    loyalty_point = make_loyalty_point(customer_id="dd4649e6-2484-4993-acb8-0f9123103394")

    # WHEN
    mocker.patch.object(app.DynamoDBStorage, "from_env", return_value=storage)
    app.lambda_handler(event=sqs_records, context=lambda_context)

    # THEN
    assert len(storage.data[loyalty_point.customerId]) == 2
