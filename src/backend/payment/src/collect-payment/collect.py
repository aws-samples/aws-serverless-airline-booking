import json
import os

import requests
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()

# Payment API Capture URL to collect payment(i.e. https://endpoint/capture)
payment_endpoint = os.environ["PAYMENT_API_URL"]


class PaymentException(Exception):
    def __init__(self, message="Payment failed", status_code=500, details={}):

        super(PaymentException, self).__init__()

        self.message = message
        self.status_code = status_code
        self.details = details


@xray_recorder.capture("## collect_payment")
def collect_payment(charge_id):
    """Collects payment from a pre-authorized charge through Payment API

    For more info on Stripe Charge Object: https://stripe.com/docs/api/charges/object

    Parameters
    ----------
    charge_id : string
        Pre-authorized charge ID received from Payment API        

    Returns
    -------
    dict
        receiptUrl: string
            receipt URL containing more details about the successful charge

        price: int
            amount collected
    """
    payment_payload = {"chargeId": charge_id}
    ret = requests.post(payment_endpoint, json=payment_payload)
    payment_response = ret.json()

    # TODO: Create decorator for tracing
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_metadata(charge_id, ret, "payment")

    if ret.status_code != 200:
        print(payment_response)
        raise PaymentException(status_code=ret.status_code, details=ret.json())

    return {
        "receiptUrl": payment_response["capturedCharge"]["receipt_url"],
        "price": payment_response["capturedCharge"]["amount"]
    }


@xray_recorder.capture("## handler")
def lambda_handler(event, context):
    """AWS Lambda Function entrypoint to collect payment

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
    dict
        receiptUrl: string
            receipt URL of charge collected

        price: int
            amount collected

    Raises
    ------
    BookingConfirmationException
        Booking Confirmation Exception including error message upon failure
    """
    if "chargeId" not in event:
        raise ValueError(message="Invalid Charge ID", status_code=400)

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", event.get("chargeId", "undefined"))
    subsegment.put_annotation("Booking", event.get('bookingId', "undefined"))
    subsegment.put_annotation("Customer", event.get('customerId', "undefined"))
    subsegment.put_annotation("Flight", event.get('outboundFlightId', "undefined"))
    subsegment.put_annotation("StateMachineExecution", event.get('name', "undefined"))

    try:
        ret = collect_payment(event["chargeId"])
        subsegment.put_annotation("PaymentStatus", "SUCCESS")
        # Step Functions can append multiple values if you return a single dict
        return ret
    except PaymentException as err:
        subsegment.put_annotation("PaymentStatus", "FAILED")
        subsegment.put_metadata("payment_error", err, "payment")
        raise PaymentException(details=err)
