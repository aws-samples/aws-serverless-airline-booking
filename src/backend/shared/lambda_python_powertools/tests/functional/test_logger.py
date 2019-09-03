import io
import json
import logging
from dataclasses import dataclass

import pytest

from lambda_python_powertools.logging import (
    MetricUnit,
    log_metric,
    logger_inject_lambda_context,
    logger_inject_process_booking_sfn,
    logger_setup,
)


@pytest.fixture
def stdout():
    return io.StringIO()


@pytest.fixture
def handler(stdout):
    return logging.StreamHandler(stdout)


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


def test_setup_service_name(root_logger, stdout):
    # GIVEN service is explicitly defined
    # WHEN logger is setup
    # THEN service field should be equals service given
    service_name = "payment"
    logger = logger_setup(service=service_name)
    logger.info("Hello")
    log = json.loads(stdout.getvalue())

    assert service_name == log["service"]


def test_setup_no_service_name(root_logger, stdout):
    # GIVEN no service is explicitly defined
    # WHEN logger is setup
    # THEN service field should be "service_undefined"
    logger_setup()
    logger = logger_setup()
    logger.info("Hello")
    log = json.loads(stdout.getvalue())

    assert "service_undefined" == log["service"]


def test_setup_service_env_var(monkeypatch, root_logger, stdout):
    # GIVEN service is explicitly defined via POWERTOOLS_SERVICE_NAME env
    # WHEN logger is setup
    # THEN service field should be equals POWERTOOLS_SERVICE_NAME value
    service_name = "payment"
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", service_name)

    logger = logger_setup()
    logger.info("Hello")
    log = json.loads(stdout.getvalue())

    assert service_name == log["service"]


def test_inject_lambda_context(root_logger, stdout, lambda_context):
    # GIVEN a lambda function is decorated with logger
    # WHEN logger is setup
    # THEN lambda contextual info should always be in the logs
    logger_context_keys = (
        "function_name",
        "function_memory_size",
        "function_arn",
        "function_request_id",
    )

    logger = logger_setup()

    @logger_inject_lambda_context
    def handler(event, context):
        logger.info("Hello")

    handler({}, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in logger_context_keys:
        assert key in log


def test_inject_lambda_context_log_event_request(root_logger, stdout, lambda_context):
    # GIVEN a lambda function is decorated with logger instructed to log event
    # WHEN logger is setup
    # THEN logger should log event received from Lambda
    lambda_event = {"greeting": "hello"}

    logger = logger_setup()

    @logger_inject_lambda_context(log_event=True)
    def handler(event, context):
        logger.info("Hello")

    handler(lambda_event, lambda_context)

    # Given that our string buffer has many log statements separated by newline \n
    # We need to clean it before we can assert on
    stdout.seek(0)
    logs = [json.loads(line.strip()) for line in stdout.readlines()]
    logged_event, _ = logs
    assert "greeting" in logged_event["message"]


def test_inject_lambda_context_log_event_request_env_var(
    monkeypatch, root_logger, stdout, lambda_context
):

    # GIVEN a lambda function is decorated with logger instructed to log event
    # via POWERTOOLS_LOGGER_LOG_EVENT env
    # WHEN logger is setup
    # THEN logger should log event received from Lambda
    lambda_event = {"greeting": "hello"}
    monkeypatch.setenv("POWERTOOLS_LOGGER_LOG_EVENT", "true")

    logger = logger_setup()

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
    monkeypatch, root_logger, stdout, lambda_context
):
    # GIVEN a lambda function is decorated with logger
    # WHEN logger is setup
    # THEN logger should not log event received by lambda handler
    lambda_event = {"greeting": "hello"}

    logger = logger_setup()

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


def test_inject_process_booking_sfn(root_logger, stdout, lambda_context):
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

    logger = logger_setup()

    @logger_inject_process_booking_sfn
    def handler(event, context):
        logger.info("Hello")

    handler(process_booking_event, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in logger_context_keys:
        assert key in log


def test_inject_process_booking_sfn_invalid(root_logger, stdout, lambda_context):
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

    logger = logger_setup()

    @logger_inject_process_booking_sfn
    def handler(event, context):
        logger.info("Hello")

    handler(lambda_event, lambda_context)

    log = json.loads(stdout.getvalue())

    for key in logger_context_keys:
        assert key in log


def test_inject_lambda_cold_start(root_logger, stdout, lambda_context):
    # GIVEN a lambda function is decorated with logger, and called twice
    # WHEN logger is setup
    # THEN cold_start key should only be true in the first call

    from lambda_python_powertools.logging import logger

    # # As we run tests in parallel global cold_start value can be false
    # # here we reset to simulate the correct behaviour
    # # since Lambda will only import our logger lib once per concurrent execution
    logger.is_cold_start = True

    logger = logger_setup()

    def custom_method():
        logger.info("Hello from method")

    @logger_inject_lambda_context
    def handler(event, context):
        custom_method()
        logger.info("Hello")

    handler({}, lambda_context)
    handler({}, lambda_context)

    # Given that our string buffer has many log statements separated by newline \n
    # We need to clean it before we can assert on
    stdout.seek(0)
    logs = [json.loads(line.strip()) for line in stdout.readlines()]
    first_log, second_log, third_log, fourth_log = logs

    # First execution
    assert "true" == first_log["cold_start"]
    assert "true" == second_log["cold_start"]

    # Second execution
    assert "false" == third_log["cold_start"]
    assert "false" == fourth_log["cold_start"]


def test_log_metric(capsys):
    # GIVEN a service, unit and value have been provided
    # WHEN log_metric is called
    # THEN custom metric line should be match given values
    log_metric(service="payment", name="test_metric", unit=MetricUnit.Seconds, value=60)
    expected = "MONITORING|60|Seconds|test_metric|ServerlessAirline|service=payment\n"
    captured = capsys.readouterr()

    assert captured.out == expected


def test_log_metric_env_var(monkeypatch, capsys):
    # GIVEN a service, unit and value have been provided
    # WHEN log_metric is called
    # THEN custom metric line should be match given values
    service_name = "payment"
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", service_name)

    log_metric(name="test_metric", unit=MetricUnit.Seconds, value=60)
    expected = "MONITORING|60|Seconds|test_metric|ServerlessAirline|service=payment\n"
    captured = capsys.readouterr()

    assert captured.out == expected


def test_log_metric_multiple_dimensions(capsys):
    # GIVEN multiple optional dimensions are provided
    # WHEN log_metric is called
    # THEN dimensions should appear as dimenion=value
    log_metric(
        name="test_metric", unit=MetricUnit.Seconds, value=60, customer="abc", charge_id="123"
    )
    expected = "MONITORING|60|Seconds|test_metric|ServerlessAirline|service=service_undefined,customer=abc,charge_id=123\n"
    captured = capsys.readouterr()

    assert captured.out == expected


@pytest.mark.parametrize(
    "invalid_input,expected",
    [
        (
            {"unit": "seconds"},
            "MONITORING|0|Seconds|test_metric|ServerlessAirline|service=service_undefined\n",
        ),
        (
            {"unit": "Seconds", "customer": None, "charge_id": "123", "payment_status": ""},
            "MONITORING|0|Seconds|test_metric|ServerlessAirline|service=service_undefined,charge_id=123\n",
        ),
    ],
    ids=["metric unit as string lower case", "empty dimension value"],
)
def test_log_metric_partially_correct_args(capsys, invalid_input, expected):
    # GIVEN invalid arguments are provided such as empty dimension values and metric units in strings
    # WHEN log_metric is called
    # THEN default values should be used such as "Count" as a unit, invalid dimensions not included
    # and no exception raised
    log_metric(name="test_metric", **invalid_input)
    captured = capsys.readouterr()

    assert captured.out == expected


@pytest.mark.parametrize(
    "invalid_input,expected",
    [({"unit": "Blah"}, ValueError), ({"unit": None}, ValueError), ({}, TypeError)],
    ids=["invalid metric unit as str", "unit as None", "missing required unit"],
)
def test_log_metric_invalid_unit(invalid_input, expected):
    # GIVEN invalid units are provided
    # WHEN log_metric is called
    # THEN ValueError exception should be raised

    with pytest.raises(expected):
        log_metric(name="test_metric", **invalid_input)
