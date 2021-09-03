import json

import boto3
import pytest
from botocore.stub import ANY, Stubber
from loyalty.ingest import app
from loyalty.shared.models import LoyaltyPoint
from loyalty.shared.storage import DynamoDBStorage


def test_add_loyalty_points(dynamodb_stub, record, transaction):
    ddb_storage, stubber = dynamodb_stub
    put_item_params = {
        "Item": {
            **DynamoDBStorage.build_add_transaction_item(item=transaction),
            "sk": ANY,
            "createdAt": ANY,
        },
        "TableName": "test",
    }
    stubber.add_response("put_item", {}, put_item_params)
    app.process_loyalty_points(record=record, storage_client=ddb_storage)


# def test_lambda_handler_can_process_sqs_records(
#     records, lambda_context, mocker, monkeypatch
# ):
#     monkeypatch.setenv("TABLE_NAME", "test")
#     ddb_storage_client = app.DynamoDBStorage.from_env()
#     app.DynamoDBStorage.from_env = mocker.MagicMock(return_value=ddb_storage_client)

#     stubber = Stubber(ddb_storage_client.client.meta.client)
#     stubber.activate()
#     transaction = LoyaltyPoint(**json.loads(records["Records"][0]["body"]))
#     put_item_params = {
#         "Item": {
#             **DynamoDBStorage.build_add_transaction_item(item=transaction),
#             "sk": ANY,
#             "createdAt": ANY,
#         },
#         "TableName": "test",
#     }
#     stubber.add_response("put_item", {}, put_item_params)

#     app.lambda_handler(event=records, context=lambda_context)

#     stubber.deactivate()
#     stubber.assert_no_pending_responses()
