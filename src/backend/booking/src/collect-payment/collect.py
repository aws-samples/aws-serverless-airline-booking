from botocore.vendored import requests
import os

class PaymentException(Exception):
    def __init__(self, message, status_code):

        # Call the base class constructor with the parameters it needs
        super(PaymentException, self).__init__(message)

        # Now for your custom code...
        self.status_code = status_code

def collect_payment(payment):
    paymentApiResponse = requests.post(os.environ['PAYMENT_API_URL'], json = { "chargeId":payment["chargeId"]})
    print(paymentApiResponse.content)
    if paymentApiResponse.status_code == 200:
        return paymentApiResponse.content
    raise PaymentException('Payment failed', paymentApiResponse.status_code)


def lambda_handler(event, context):
    collect_payment(event)


