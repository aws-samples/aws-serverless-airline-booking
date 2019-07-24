import json
import logging
import os

import aws_lambda_logging
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
    logging.info("Collecting payment...")
    ret = requests.post(payment_endpoint, json=payment_payload)
    payment_response = ret.json()

    # TODO: Create decorator for tracing
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_metadata(charge_id, ret, "payment")

    if ret.status_code != 200:
        print(payment_response)
        logging.error("Failed to collect payment")
        raise PaymentException(status_code=ret.status_code, details=ret.json())

    return {
        "receiptUrl": payment_response["capturedCharge"]["receipt_url"],
        "price": payment_response["capturedCharge"]["amount"],
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

    customer_id = event.get("customerId", "undefined")
    booking_id = event.get("bookingId", "undefined")
    charge_id = event.get("chargeId", "undefined")
    state_machine_execution_id = event.get("name", "undefined")

    aws_lambda_logging.setup(
        level=os.getenv("LOG_LEVEL", "INFO"),
        lambda_request_id=context.aws_request_id,
        lambda_arn=context.invoked_function_arn,
        service="payment",
        customer_id=customer_id,
        booking_id=booking_id,
        charge_id=charge_id,
    )

    if "chargeId" not in event:
        logging.error("Invalid event")
        logging.info(event)
        raise ValueError(message="Invalid Charge ID", status_code=400)

    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation("Payment", charge_id)
    subsegment.put_annotation("Booking", booking_id)
    subsegment.put_annotation("Customer", customer_id)
    subsegment.put_annotation("Flight", event.get("outboundFlightId", "undefined"))
    subsegment.put_annotation("StateMachineExecution", state_machine_execution_id)

    try:
        ret = collect_payment(charge_id)
        logging.info("Payment has been successful")
        subsegment.put_annotation("PaymentStatus", "SUCCESS")
        # Step Functions can append multiple values if you return a single dict
        return ret
    except PaymentException as err:
        subsegment.put_annotation("PaymentStatus", "FAILED")
        subsegment.put_metadata("payment_error", err, "payment")
        raise PaymentException(details=err)
