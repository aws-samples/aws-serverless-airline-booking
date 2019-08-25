import io
import json
import logging
from dataclasses import dataclass

import pytest

from lambda_python_powertools.logging import (
    logger_inject_lambda_context,
    logger_setup,
    logger_inject_process_booking_sfn,
)


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
    logger_context_keys = (
        "function_name",
        "function_memory_size",
        "function_arn",
        "function_request_id",
    )

    logger_setup()

    @logger_inject_lambda_context
    def handler(event, context):
        logger.info("Hello")

    handler({}, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in logger_context_keys:
        assert key in log


def test_inject_lambda_context_log_event_request(root_logger, logger, stdout, lambda_context):
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
    monkeypatch, root_logger, logger, stdout, lambda_context
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
    monkeypatch, root_logger, logger, stdout, lambda_context
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


def test_inject_process_booking_sfn(root_logger, logger, stdout, lambda_context):
    # GIVEN a lambda function is decorated with process booking logger
    # WHEN logger is setup
    # THEN lambda and process booking contextual info should always be in the logs
    logger_context_keys = (
        "function_name",
        "function_memory_size",
        "function_arn",
        "function_request_id",
        "outbound_flight_id",
        "customer_id",
        "charge_id",
        "state_machine_execution_id",
        "booking_id",
    )

    process_booking_event = {
        "outboundFlightId": "1688a4f6-69dd-4590-833e-f349384df465",
        "customerId": "d749f277-0950-4ad6-ab04-98988721e475",
        "chargeId": "ch_1F57JxF4aIiftV70vM1BRI5Z",
        "bookingTable": "Booking-2pa2xn3qzzdi7ntbhdozirkmiy-twitch",
        "flightTable": "Flight-2pa2xn3qzzdi7ntbhdozirkmiy-twitch",
        "name": "7e5ecef7-84c4-4836-9500-2115c4175421",
        "createdAt": "2019-08-08T08:50:06.362Z",
        "bookingId": "f0fc04ca-a125-45cd-8c37-d09210d7a560",
        "payment": {
            "receiptUrl": "https://pay.stripe.com/receipts/acct_1Dvn7pF4aIiftV70/ch_1F57JxF4aIiftV70vM1BRI5Z/rcpt_FaHtr7NWaZuHsZPEfkqWX5UbKTGIL25",
            "price": 100,
        },
        "bookingReference": "YvSY1Q",
        "notificationId": "4f984180-ad27-56db-8606-144549af6806",
    }

    logger_setup()

    @logger_inject_process_booking_sfn
    def handler(event, context):
        logger.info("Hello")

    handler(process_booking_event, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in logger_context_keys:
        assert key in log


def test_inject_process_booking_sfn_invalid(root_logger, logger, stdout, lambda_context):
    # GIVEN a lambda function is decorated with process booking logger
    # WHEN logger is setup but event doesn't come from process booking state machine
    # THEN only lambda should be in the logs and no exceptions raised
    logger_context_keys = (
        "function_name",
        "function_memory_size",
        "function_arn",
        "function_request_id",
    )

    lambda_event = {"some": "value"}

    logger_setup()

    @logger_inject_process_booking_sfn
    def handler(event, context):
        logger.info("Hello")

    handler(lambda_event, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in logger_context_keys:
        assert key in log
