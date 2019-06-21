import json
import os

from botocore.vendored import requests

# Payment API Capture URL to collect payment(i.e. https://endpoint/capture)
payment_endpoint = os.environ["PAYMENT_API_URL"]


class PaymentException(Exception):
    def __init__(self, message, status_code):

        super(PaymentException, self).__init__(message)
        self.status_code = status_code


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

    if ret.status_code != 200:
        print(payment_response)
        raise PaymentException("Payment failed", ret.status_code)

    return {
        "receiptUrl": payment_response["capturedCharge"]["receipt_url"],
        "price": payment_response["capturedCharge"]["amount"]
    }


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

    ret = collect_payment(event["chargeId"])

    # Step Functions can append multiple values if you return a single dict
    return ret
