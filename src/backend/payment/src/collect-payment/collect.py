import os

import requests
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

from process_booking import process_booking_handler

logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Payment API Capture URL to collect payment(i.e. https://endpoint/capture)
payment_endpoint = os.getenv("PAYMENT_API_URL")


class PaymentException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Payment failed"
        self.details = details or {}


@tracer.capture_method
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
    if not payment_endpoint:
        logger.error({"operation": "input_validation", "details": os.environ})
        raise ValueError("Payment API URL is invalid -- Consider reviewing PAYMENT_API_URL env")

    payment_payload = {"chargeId": charge_id}

    try:
        logger.debug({"operation": "payment_collection", "details": payment_payload})
        ret = requests.post(payment_endpoint, json=payment_payload)
        ret.raise_for_status()

        payment_response = ret.json()
        tracer.put_metadata(charge_id, ret)
        logger.info(
            {
                "operation": "payment_collection",
                "details": {
                    "response_headers": ret.headers,
                    "response_payload": payment_response,
                    "response_status_code": ret.status_code,
                    "url": ret.url,
                },
            }
        )

        return {
            "receiptUrl": payment_response["capturedCharge"]["receipt_url"],
            "price": payment_response["capturedCharge"]["amount"],
        }
    except requests.exceptions.RequestException as err:
        logger.exception({"operation": "payment_collection"})
        raise PaymentException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@process_booking_handler(logger=logger)
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
    pre_authorization_token = event.get("chargeId")
    customer_id = event.get("customerId")

    if not pre_authorization_token:
        metrics.add_metric(name="InvalidPaymentRequest", unit=MetricUnit.Count, value=1)
        logger.error({"operation": "input_validation", "details": event})
        raise ValueError("Invalid Charge ID")

    try:
        logger.debug(
            f"Collecting payment from customer {customer_id} using {pre_authorization_token} token"
        )
        ret = collect_payment(pre_authorization_token)
        metrics.add_metric(name="SuccessfulPayment", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("PaymentStatus", "SUCCESS")

        return ret  # Step Functions can append multiple values if you return a single dict
    except PaymentException as err:
        metrics.add_metric(name="FailedPayment", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("PaymentStatus", "FAILED")
        logger.exception({"operation": "payment_collection"})
        raise
