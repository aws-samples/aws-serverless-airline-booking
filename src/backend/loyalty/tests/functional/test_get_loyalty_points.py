from loyalty.get import app
from loyalty.shared.models import LoyaltyPoint


def test_get_loyalty_points(dynamodb_stub, transaction: LoyaltyPoint):
    ddb_storage, stubber = dynamodb_stub
    get_item_params = {
        "Key": {"pk": f"CUSTOMER#{transaction.customerId}", "sk": "AGGREGATE"},
        "AttributesToGet": ["total_points", "tier"],
        "TableName": "test",
    }
    stubber.add_response("get_item", {}, get_item_params)
    app.get_loyalty_points(customer_id=transaction.customerId, storage_client=ddb_storage)
