import os

import requests
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

from process_booking import process_booking_handler

logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Payment API Capture URL to refund payment(i.e. https://endpoint/refund)
payment_endpoint = os.getenv("PAYMENT_API_URL")


class RefundException(Exception):
    def __init__(self, message=None, details=None):
        self.message = message or "Refund failed"
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
        logger.error({"operation": "input_validation", "details": os.environ})
        raise ValueError("Payment API URL is invalid -- Consider reviewing PAYMENT_API_URL env")

    refund_payload = {"chargeId": charge_id}

    try:
        logger.debug({"operation": "payment_refund", "details": refund_payload})
        ret = requests.post(payment_endpoint, json=refund_payload)
        ret.raise_for_status()
        
        refund_response = ret.json()
        tracer.put_metadata(charge_id, ret.json())
        logger.info(
            {
                "operation": "payment_refund",
                "details": {
                    "response_headers": ret.headers,
                    "response_payload": refund_response,
                    "response_status_code": ret.status_code,
                    "url": ret.url,
                },
            }
        )
        
        return {"refundId": refund_response["createdRefund"]["id"]}
    except requests.exceptions.RequestException as err:
        logger.exception({"operation": "payment_refund"})
        raise RefundException(details=err)


@metrics.log_metrics(capture_cold_start_metric=True)
@process_booking_handler(logger=logger)
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
    payment_token = event.get("chargeId")
    customer_id = event.get("customerId")

    if not payment_token:
        metrics.add_metric(name="InvalidRefundRequest", unit=MetricUnit.Count, value=1)
        logger.error({"operation": "input_validation", "details": event})
        raise ValueError("Invalid Charge ID")

    try:
        logger.debug(f"Refunding payment from customer {customer_id} using {payment_token} token")
        ret = refund_payment(payment_token)

        metrics.add_metric(name="SuccessfulRefund", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("Refund", ret["refundId"])
        tracer.put_annotation("PaymentStatus", "REFUNDED")

        return ret
    except RefundException as err:
        metrics.add_metric(name="FailedRefund", unit=MetricUnit.Count, value=1)
        tracer.put_annotation("RefundStatus", "FAILED")
        logger.exception({"operation": "payment_refund"})
        raise
