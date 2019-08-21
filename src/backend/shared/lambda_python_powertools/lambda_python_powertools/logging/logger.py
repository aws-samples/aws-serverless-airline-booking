import functools
import logging
import os
from typing import Any, Callable, Dict

import aws_lambda_logging


def logger_setup(service: str = "service_undefined", level: str = "INFO", **kwargs):
    service = os.getenv("POWERTOOLS_SERVICE_NAME") or service
    aws_lambda_logging.setup(level=level, service=service, **kwargs)


def logger_inject_lambda_context(
    lambda_handler: Callable[[Dict, Any], Any] = None, log_event: bool = False
):

    logger = logging.getLogger(__name__)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    # If handler is None we've been called with parameters
    # We then return a partial function with args filled
    # Next time we're called we'll call our Lambda
    # This allows us to avoid writing wrapper_wrapper type of fn
    if lambda_handler is None:
        logger.debug("Decorator called with parameters")
        return functools.partial(logger_inject_lambda_context, log_event=log_event)

    @functools.wraps(lambda_handler)
    def decorate(event, context):
        if log_event:
            logger.debug("Event received")
            logger.info(event)

        lambda_context = _capture_lambda_context(event, context)
        logger_setup(**lambda_context)

        return lambda_handler(event, context)

    return decorate


def _capture_lambda_context(event: Dict, context: object) -> Dict:

    fn_name = getattr(context, "function_name", "")
    memory_size = str(getattr(context, "memory_limit_in_mb", ""))
    fn_arn = getattr(context, "invoked_function_arn", "")
    request_id = getattr(context, "aws_request_id", "")

    lambda_context = {
        "lambda_function_name": fn_name,
        "lambda_function_memory_size": memory_size,
        "lambda_function_arn": fn_arn,
        "lambda_request_id": request_id,
    }

    return lambda_context
