from lambda_python_powertools.tracing import capture_booking_state_machine


@capture_booking_state_machine
def handler(event, context):
    print("Received event from Lambda...")

    return "Resolved"


handler({}, {})
