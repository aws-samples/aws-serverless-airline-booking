from botocore.vendored import requests
import os

class RefundException(Exception):
    def __init__(self, message, status_code):

        # Call the base class constructor with the parameters it needs
        super(RefundException, self).__init__(message)

        # Now for your custom code...
        self.status_code = status_code

def refund_payment(charge):
    paymentApiResponse = requests.post(os.environ['PAYMENT_API_URL'], json = { "chargeId":charge["chargeId"]})
    print(paymentApiResponse.content)

    if paymentApiResponse.status_code == 200:
        return { 
            paymentApiResponse.content
        }
    raise RefundException('Refund failed.', paymentApiResponse.status_code)

def lambda_handler(event, context):
    refund_payment(event)
