import json
import os

import requests
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()

# Payment API Refund URL to collect payment(i.e. https://endpoint/refund)
payment_endpoint = os.environ["PAYMENT_API_URL"]


class RefundException(Exception):
    def __init__(self, message="Refund failed", status_code=500, details={}):

        super(RefundException, self).__init__()

        self.message = message
        self.status_code = status_code
        self.details = details


@xray_recorder.capture("## refund_payment")
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

    # TODO: Create decorator for tracing
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_metadata(charge_id, ret, "refund")

    if ret.status_code != 200:
        print(refund_response)
        raise RefundException(status_code=ret.status_code, details=ret.json())

    return {"refundId": refund_response["createdRefund"]["id"]}


@xray_recorder.capture("## handler")
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

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", event.get("chargeId", "undefined"))
    subsegment.put_annotation("Booking", event.get("bookingId", "undefined"))
    subsegment.put_annotation("Customer", event.get("customerId", "undefined"))
    subsegment.put_annotation("Flight", event.get("outboundFlightId", "undefined"))
    subsegment.put_annotation("StateMachineExecution", event.get("name", "undefined"))

    try:
        ret = refund_payment(event["chargeId"])
        subsegment.put_annotation("Refund", ret["refundId"])
        subsegment.put_annotation("PaymentStatus", "REFUNDED")
    except RefundException as err:
        subsegment.put_metadata("refund_error", err, "refund")
        subsegment.put_annotation("RefundStatus", "FAILED")
        raise RefundException(details=err)

    return json.dumps(ret)
