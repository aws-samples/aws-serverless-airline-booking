import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_mock import MockerFixture

from loyalty.ingest import app
from loyalty.shared.models import LoyaltyPoint
from loyalty.shared.storage import FakeStorage


def test_process_loyalty_points(record, transaction: LoyaltyPoint):
    storage = FakeStorage()
    app.process_loyalty_points(record=record, storage_client=storage)
    assert transaction in storage


def test_add_loyalty_points_invalid_record(record, monkeypatch):
    monkeypatch.setenv("LOYALTY_TABLE_NAME", "test")
    record["body"] = '{"customerId":"1234","price":100}'  # old payload
    with pytest.raises(ValueError, match="Invalid payload"):
        app.process_loyalty_points(record=record)


def test_handler_process_sqs_event(
    sqs_records: dict, transaction: LoyaltyPoint, lambda_context: LambdaContext, mocker: MockerFixture
):
    storage = FakeStorage()
    app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=storage)  # type: ignore
    customer_id = transaction.customerId

    app.lambda_handler(event=sqs_records, context=lambda_context)
    assert len(storage.data[customer_id]) == 2
