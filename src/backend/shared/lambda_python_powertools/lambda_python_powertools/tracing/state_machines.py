import functools


def capture_booking_state_machine(lambda_handler=None, service=None):
    # If handler is None we've been called with a service name
    # We then return a partial function with service filled
    # Next time we're called we'll call our Lambda
    # This allows us to avoid writing wrapper_wrapper type of fn
    if lambda_handler is None:
        return functools.partial(capture_booking_state_machine, service=service)

    @functools.wraps(lambda_handler)
    def decorate(event, context):
        if service:
            print(f"Service that we received: {service}")
        print(f"Received event: {event}")
        print(f"Received context: {context}")

        response = lambda_handler(event, context)

        return response

    return decorate

