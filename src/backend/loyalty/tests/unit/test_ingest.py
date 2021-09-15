import json

import pytest

from loyalty.ingest import app
from loyalty.shared.storage import FakeStorage


def test_process_loyalty_points(record, transaction):
    storage = FakeStorage()
    app.process_loyalty_points(record=record, storage_client=storage)
    assert transaction in storage


def test_add_loyalty_points_invalid_record(record, monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "test")
    record["body"] = '{"customerId":"1234","price":100}'  # old payload
    with pytest.raises(ValueError, match="Invalid payload"):
        app.process_loyalty_points(record=record)


def test_handler_process_sqs_event(records, mocker, lambda_context):
    storage = FakeStorage()
    app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=storage)
    customer_id = json.loads(records["Records"][0]["body"])["customerId"]

    app.lambda_handler(event=records, context=lambda_context)
    assert len(storage.data[customer_id]) == 2
