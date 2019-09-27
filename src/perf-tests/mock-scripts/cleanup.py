import boto3
import csv
import os
import json

AWS_REGION = os.environ['AWS_REGION']
TOKEN_CSV = os.environ['PATH'] + os.environ['TOKEN_CSV']
USER_CSV = os.environ['PATH'] + os.environ['USER_CSV']
S3_BUCKET = os.environ['S3_BUCKET']
USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

client = boto3.client('cognito-idp', region_name=AWS_REGION)
s3 = boto3.client('s3')

try:
    with open(USER_CSV, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader, None)
            for row in csv_reader:
                response = client.admin_delete_user(
                    UserPoolId= USER_POOL_ID,
                    Username= row[0]
                )
except Exception as error:
    pass
    print(f'Error - {error}')
