import io
import json
import logging
from dataclasses import dataclass

import pytest

from lambda_python_powertools.logging import logger_inject_lambda_context, logger_setup


@pytest.fixture
def stdout():
    return io.StringIO()


@pytest.fixture
def handler(stdout):
    return logging.StreamHandler(stdout)


@pytest.fixture
def logger():
    return logging.getLogger(__name__)


@pytest.fixture
def root_logger(handler):
    logging.root.addHandler(handler)
    yield logging.root
    logging.root.removeHandler(handler)


@pytest.fixture
def lambda_context():
    @dataclass
    class Context:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return Context()


def test_setup_service_name(root_logger, logger, stdout):
    # GIVEN service is explicitly defined
    # WHEN logger is setup
    # THEN service field should be equals service given
    service_name = "payment"
    logger_setup(service=service_name)
    logger.info("Hello")
    log = json.loads(stdout.getvalue())

    assert service_name == log["service"]


def test_setup_no_service_name(root_logger, logger, stdout):
    # GIVEN no service is explicitly defined
    # WHEN logger is setup
    # THEN service field should be "service_undefined"
    logger_setup()
    logger.info("Hello")
    log = json.loads(stdout.getvalue())

    assert "service_undefined" == log["service"]


def test_setup_service_env_var(monkeypatch, root_logger, logger, stdout):
    # GIVEN service is explicitly defined via POWERTOOLS_SERVICE_NAME env
    # WHEN logger is setup
    # THEN service field should be equals POWERTOOLS_SERVICE_NAME value
    service_name = "payment"
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", service_name)

    logger_setup(service=service_name)
    logger.info("Hello")
    log = json.loads(stdout.getvalue())

    assert service_name == log["service"]


def test_inject_lambda_context(root_logger, logger, stdout, lambda_context):
    # GIVEN a lambda function is decorated with logger
    # WHEN logger is setup
    # THEN lambda contextual info should always be in the logs
    lambda_context_keys = (
        "lambda_function_arn",
        "lambda_function_memory_size",
        "lambda_function_arn",
        "lambda_request_id",
    )

    logger_setup()

    @logger_inject_lambda_context
    def handler(event, context):
        logger.info("Hello")

    handler({}, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in lambda_context_keys:
        assert key in log


def test_inject_lambda_context_log_event_request(root_logger, logger, stdout):
    # GIVEN a lambda function is decorated with logger instructed to log event
    # WHEN logger is setup
    # THEN logger should log event received from Lambda
    lambda_event = {"greeting": "hello"}

    logger_setup()

    @logger_inject_lambda_context(log_event=True)
    def handler(event, context):
        logger.info("Hello")

    handler(lambda_event, lambda_context)

    # Given that our string buffer has many log statements separated by newline \n
    # We need to clean it before we can assert on
    stdout.seek(0)
    logs = [json.loads(line.strip()) for line in stdout.readlines()]

    event = {}
    for log in logs:
        if "greeting" in log["message"]:
            event = log["message"]

    assert event == lambda_event


def test_inject_lambda_context_log_event_request_env_var(
    monkeypatch, root_logger, logger, stdout
):

    # GIVEN a lambda function is decorated with logger instructed to log event
    # via POWERTOOLS_LOGGER_LOG_EVENT env
    # WHEN logger is setup
    # THEN logger should log event received from Lambda
    lambda_event = {"greeting": "hello"}
    monkeypatch.setenv("POWERTOOLS_LOGGER_LOG_EVENT", "true")

    logger_setup()

    @logger_inject_lambda_context()
    def handler(event, context):
        logger.info("Hello")

    handler(lambda_event, lambda_context)

    # Given that our string buffer has many log statements separated by newline \n
    # We need to clean it before we can assert on
    stdout.seek(0)
    logs = [json.loads(line.strip()) for line in stdout.readlines()]

    event = {}
    for log in logs:
        if "greeting" in log["message"]:
            event = log["message"]

    assert event == lambda_event


def test_inject_lambda_context_log_no_request_by_default(
    monkeypatch, root_logger, logger, stdout
):
    # GIVEN a lambda function is decorated with logger
    # WHEN logger is setup
    # THEN logger should not log event received by lambda handler
    lambda_event = {"greeting": "hello"}

    logger_setup()

    @logger_inject_lambda_context()
    def handler(event, context):
        logger.info("Hello")

    handler(lambda_event, lambda_context)

    # Given that our string buffer has many log statements separated by newline \n
    # We need to clean it before we can assert on
    stdout.seek(0)
    logs = [json.loads(line.strip()) for line in stdout.readlines()]

    event = {}
    for log in logs:
        if "greeting" in log["message"]:
            event = log["message"]

    assert event != lambda_event
