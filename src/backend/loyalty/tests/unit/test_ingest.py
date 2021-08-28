from pathlib import Path
from ingest import app
from tests.conftest import load_event
from botocore.stub import Stubber, ANY
import pytest
import json

ingest_event_file = Path("tests/events/ingest_event.json")


@pytest.fixture(autouse=True)
def dynamodb_stub():
    stubber = Stubber(app.dynamodb.meta.client)
    stubber.activate()
    yield stubber
    stubber.deactivate()
    stubber.assert_no_pending_responses()


def test_add_loyalty_points(lambda_context, dynamodb_stub):
    event = load_event(filepath=ingest_event_file)
    record = json.loads(event["Records"][0]["body"])

    put_item_params = {
        "Item": {
            "bookingDetails": record.get("bookingDetails"),
            "createdAt": ANY,
            "outboundFlightId": record.get("outboundFlightId"),
            "paymentDetails": record.get("paymentDetails"),
            "pk": record.get("customerId"),
            "points": 100,
            "sk": ANY,
            "status": "ACTIVE",
            "tier": "BRONZE",
        },
        "TableName": "undefined",
    }
    dynamodb_stub.add_response("put_item", {}, put_item_params)

    app.lambda_handler(event, lambda_context)
