import os

import requests

from lambda_python_powertools.logging import (
    MetricUnit,
    log_metric,
    logger_inject_process_booking_sfn,
    logger_setup,
)
from lambda_python_powertools.tracing import Tracer

logger = logger_setup()
tracer = Tracer()

_cold_start = True

# Payment API Capture URL to collect payment(i.e. https://endpoint/capture)
payment_endpoint = os.getenv("PAYMENT_API_URL")


class PaymentException(Exception):
    def __init__(self, message=None, status_code=None, details=None):
        super(PaymentException, self).__init__()

        self.message = message or "Payment failed"
        self.status_code = status_code or 500
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
        logger.error({"operation": "invalid_config", "details": os.environ})
        raise ValueError("Payment API URL is invalid -- Consider reviewing PAYMENT_API_URL env")

    payment_payload = {"chargeId": charge_id}

    try:
        logger.debug({"operation": "collect_payment", "details": payment_payload})
        ret = requests.post(payment_endpoint, json=payment_payload)
        ret.raise_for_status()
        logger.info(
            {
                "operations": "collect_payment",
                "details": {
                    "response_headers": ret.headers,
                    "response_payload": ret.json(),
                    "response_status_code": ret.status_code,
                    "url": ret.url,
                },
            }
        )
        payment_response = ret.json()

        logger.debug("Adding collect payment operation result as tracing metadata")
        tracer.put_metadata(charge_id, ret)

        return {
            "receiptUrl": payment_response["capturedCharge"]["receipt_url"],
            "price": payment_response["capturedCharge"]["amount"],
        }
    except requests.exceptions.RequestException as err:
        logger.error({"operation": "collect_payment", "details": err})
        raise PaymentException(status_code=ret.status_code, details=err)


@tracer.capture_lambda_handler(process_booking_sfn=True)
@logger_inject_process_booking_sfn
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
    global _cold_start
    if _cold_start:
        log_metric(
            name="ColdStart", unit=MetricUnit.Count, value=1, function_name=context.function_name
        )
        _cold_start = False

    pre_authorization_token = event.get("chargeId")
    customer_id = event.get("customerId")

    if not pre_authorization_token:
        log_metric(
            name="InvalidPaymentRequest",
            unit=MetricUnit.Count,
            value=1,
            operation="collect_payment",
        )
        logger.error({"operation": "invalid_event", "details": event})
        raise ValueError("Invalid Charge ID")

    try:
        logger.debug(
            f"Collecting payment from customer {customer_id} using {pre_authorization_token} token"
        )
        ret = collect_payment(pre_authorization_token)

        log_metric(name="SuccessfulPayment", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Payment Status annotation")
        tracer.put_annotation("PaymentStatus", "SUCCESS")

        # Step Functions can append multiple values if you return a single dict
        return ret
    except PaymentException as err:
        log_metric(name="FailedPayment", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Payment Status annotation before raising error")
        tracer.put_annotation("PaymentStatus", "FAILED")
        logger.error({"operation": "collect_payment", "details": err})
        raise PaymentException(details=err)
