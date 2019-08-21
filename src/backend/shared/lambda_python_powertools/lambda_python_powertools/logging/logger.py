import functools
import logging
import os
from distutils.util import strtobool
from typing import Any, Callable, Dict

import aws_lambda_logging


def logger_setup(service: str = "service_undefined", level: str = "INFO", **kwargs):
    """Setups root logger to format statements in JSON.

    Includes service name and any additional key=value into logs
    It also accepts both service name or level explicitly via env vars

    Environment variables
    ---------------------
    POWERTOOLS_SERVICE_NAME : str
        service name
    LOG_LEVEL: str
        logging level (e.g. INFO, DEBUG)

    Parameters
    ----------
    service : str, optional
        service name to be appended in logs, by default "service_undefined"
    level : str, optional
        logging.level, by default "INFO"

    Example
    -------
    Setups structured logging in JSON for Lambda functions

        >>> from lambda_python_powertools.logging import logger_setup
        >>> import logging
        >>>
        >>> logger = logging.getLogger(__name__)
        >>> logging.setLevel(logging.INFO)
        >>> logger_setup()
        >>>
        >>> def handler(event, context):
                logger.info("Hello")
    """
    service = os.getenv("POWERTOOLS_SERVICE_NAME") or service
    aws_lambda_logging.setup(level=level, service=service, **kwargs)


def logger_inject_lambda_context(
    lambda_handler: Callable[[Dict, Any], Any] = None, log_event: bool = False
):
    """Decorator to capture Lambda contextual info and inject into struct logging

    Parameters
    ----------
    log_event : bool, optional
        Instructs logger to log Lambda Event, by default False

    Environment variables
    ---------------------
    POWERTOOLS_LOGGER_LOG_EVENT : str
        instruct logger to log Lambda Event (e.g. "true", "True", "TRUE")

    Example
    -------
    Captures Lambda contextual runtime info (e.g memory, arn, req_id)
        >>> from lambda_python_powertools.logging import logger_setup, logger_inject_lambda_context
        >>> import logging
        >>>
        >>> logger = logging.getLogger(__name__)
        >>> logging.setLevel(logging.INFO)
        >>> logger_setup()
        >>>
        >>> @logger_inject_lambda_context
        >>> def handler(event, context):
                logger.info("Hello")

    Captures Lambda contextual runtime info and logs incoming request
        >>> from lambda_python_powertools.logging import logger_setup, logger_inject_lambda_context
        >>> import logging
        >>>
        >>> logger = logging.getLogger(__name__)
        >>> logging.setLevel(logging.INFO)
        >>> logger_setup()
        >>>
        >>> @logger_inject_lambda_context(log_event=True)
        >>> def handler(event, context):
                logger.info("Hello")

    Returns
    -------
    decorate : Callable
        Decorated lambda handler
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    # If handler is None we've been called with parameters
    # We then return a partial function with args filled
    # Next time we're called we'll call our Lambda
    # This allows us to avoid writing wrapper_wrapper type of fn
    if lambda_handler is None:
        logger.debug("Decorator called with parameters")
        return functools.partial(logger_inject_lambda_context, log_event=log_event)

    log_event_env_option = str(os.getenv("POWERTOOLS_LOGGER_LOG_EVENT", "false"))
    log_event = strtobool(log_event_env_option) or log_event

    @functools.wraps(lambda_handler)
    def decorate(event, context):
        if log_event:
            logger.debug("Event received")
            logger.info(event)

        lambda_context = _capture_lambda_context(context)
        logger_setup(**lambda_context)

        return lambda_handler(event, context)

    return decorate


def _capture_lambda_context(context: object) -> Dict:
    """Captures Lambda function runtime info to be used across all log statements

    Parameters
    ----------
    context : object
        Lambda context object

    Returns
    -------
    Dict
        Lambda context with key fields
    """

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
