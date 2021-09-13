from loyalty.aggregate import app
from loyalty.shared.storage import FakeStorage


def test_handler(mocker, aggregate_records, lambda_context):
    storage = FakeStorage()
    app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=storage)
    app.lambda_handler(event=aggregate_records, context=lambda_context)


# Test for MODIFY events
# Test for INSERT only
# Test for INSERT + REMOVE
# Test for ConditionalCheckFailedException

# TODO: Improve traceability
### Correlation ID (X-ray)

# TODO: Update FakeStorage with new aggregate methods
