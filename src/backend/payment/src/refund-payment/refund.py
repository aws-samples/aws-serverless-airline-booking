import json
import os

from botocore.vendored import requests

# Payment API Refund URL to collect payment(i.e. https://endpoint/refund)
payment_endpoint = os.environ["PAYMENT_API_URL"]


class RefundException(Exception):
    def __init__(self, message, status_code):

        # Call the base class constructor with the parameters it needs
        super(RefundException, self).__init__(message)

        # Now for your custom code...
        self.status_code = status_code


def refund_payment(charge_id):
    """Refunds payment from a given charge ID through Payment API

    For more info on Stripe Refund Object: https://stripe.com/docs/api/refunds/object

    Parameters
    ----------
    charge_id : string
        Pre-authorized charge ID received from Payment API

    Returns
    -------
    dict
        refundId: string
    """
    refund_payload = {"chargeId": charge_id}
    ret = requests.post(payment_endpoint, json=refund_payload)
    refund_response = ret.json()

    if ret.status_code != 200:
        print(refund_response)
        raise RefundException("Refund failed", ret.status_code)

    return {"refundId": refund_response["createdRefund"]["id"]}


def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to refund payment

    Parameters
    ----------
    event: dict, required
        Step Functions State Machine event

        chargeId: string
            pre-authorization charge ID

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    -------
    string
        JSON Stringified data containing refundId ID

    Raises
    ------
    RefundException
        Refund Exception including error message upon failure
    """
    if "chargeId" not in event:
        raise RefundException(message="Invalid Charge ID", status_code=400)

    ret = refund_payment(event["chargeId"])

    return json.dumps(ret)
