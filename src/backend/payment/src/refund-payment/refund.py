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


# Payment API Capture URL to collect payment(i.e. https://endpoint/capture)
payment_endpoint = os.getenv("PAYMENT_API_URL")

_cold_start = True


class RefundException(Exception):
    def __init__(self, message=None, status_code=None, details=None):

        super(RefundException, self).__init__()

        self.message = message or "Refund failed"
        self.status_code = status_code or 500
        self.details = details or {}


@tracer.capture_method
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

    if not payment_endpoint:
        logger.error({"operation": "invalid_config", "details": os.environ})
        raise ValueError("Payment API URL is invalid -- Consider reviewing PAYMENT_API_URL env")

    refund_payload = {"chargeId": charge_id}

    try:
        logger.debug({"operation": "refund_payment", "details": refund_payload})
        ret = requests.post(payment_endpoint, json=refund_payload)
        ret.raise_for_status()
        logger.info(
            {
                "operations": "refund_payment",
                "details": {
                    "response_headers": ret.headers,
                    "response_payload": ret.json(),
                    "response_status_code": ret.status_code,
                    "url": ret.url,
                },
            }
        )
        refund_response = ret.json()

        logger.debug("Adding refund payment operation result as tracing metadata")
        tracer.put_metadata(charge_id, ret.json())

        return {"refundId": refund_response["createdRefund"]["id"]}
    except requests.exceptions.RequestException as err:
        logger.error({"operation": "collect_payment", "details": err})
        raise RefundException(status_code=ret.status_code, details=err)


@tracer.capture_lambda_handler(process_booking_sfn=True)
@logger_inject_process_booking_sfn
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

    global _cold_start
    if _cold_start:
        log_metric(
            name="ColdStart", unit=MetricUnit.Count, value=1, function_name=context.function_name
        )
        _cold_start = False

    payment_token = event.get("chargeId")
    customer_id = event.get("customerId")

    if not payment_token:
        log_metric(
            name="InvalidPaymentRequest", unit=MetricUnit.Count, value=1, operation="refund_payment"
        )
        logger.error({"operation": "invalid_event", "details": event})
        raise ValueError("Invalid Charge ID")

    try:
        logger.debug(f"Refunding payment from customer {customer_id} using {payment_token} token")
        ret = refund_payment(payment_token)

        log_metric(name="SuccessfulRefund", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Payment Refund Status annotation")
        tracer.put_annotation("Refund", ret["refundId"])
        tracer.put_annotation("PaymentStatus", "REFUNDED")

        return ret
    except RefundException as err:
        log_metric(name="FailedRefund", unit=MetricUnit.Count, value=1)
        logger.debug("Adding Payment Refund Status annotation before raising error")
        tracer.put_annotation("RefundStatus", "FAILED")
        logger.error({"operation": "refund_payment", "details": err})
        raise RefundException(details=err)
