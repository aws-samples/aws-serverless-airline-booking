import boto3
import csv
import os
import json

AWS_REGION = os.environ['AWS_REGION']
TOKEN_CSV = os.environ['FOLDERPATH'] + os.environ['TOKEN_CSV']
USER_CSV = os.environ['FOLDERPATH'] + os.environ['USER_CSV']
S3_BUCKET = os.environ['S3_BUCKET']
USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

client = boto3.client('cognito-idp', region_name=AWS_REGION)
s3 = boto3.client('s3')

if os.path.exists(TOKEN_CSV):
    os.remove(TOKEN_CSV)

try:
    # creates the users from user.csv

    with open(USER_CSV, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader, None)
            for row in csv_reader:
                createUserResponse = client.admin_create_user(
                    UserPoolId=USER_POOL_ID,
                    Username=row[0],
                    UserAttributes=[{
                        'Name': "email",
                        'Value': row[4]
                    },  
                    {
                        'Name': "phone_number",
                        'Value': row[5]
                    }
                    ],
                    MessageAction='SUPPRESS'
                )

                setUserPasswordResponse = client.admin_set_user_password(
                    UserPoolId=USER_POOL_ID,
                    Username=row[0],
                    Password=row[1],
                    Permanent=True
                )
    print(f'=== completed setting up users ===')

    # Need to enable the ADMIN_NO_SRP_AUTH on the user pool else the
    # AdminInitiateAuth operation fails with error - Auth flow not enabled for this client

    updateUserPool = client.update_user_pool_client(
        UserPoolId = USER_POOL_ID,
        ClientId = CLIENT_ID,
        ExplicitAuthFlows=['ADMIN_NO_SRP_AUTH']
    )

     # This simulates login and generates access token which is later uploaded to an S3
     # that is used in Gatling scripts 

    with open(TOKEN_CSV, mode='a') as csv_file:

        writer = csv.writer(csv_file, delimiter=',')
        header = ['username', 'token']
        writer.writerow(header)

        print("Reading the user.csv file ...")
        print("Now generating access tokens...")

        with open(USER_CSV, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader, None)
            for row in csv_reader:
                response = client.admin_initiate_auth(
                    UserPoolId= USER_POOL_ID,
                    ClientId= CLIENT_ID,
                    AuthFlow='ADMIN_NO_SRP_AUTH',
                    AuthParameters={
                            'USERNAME': row[0],
                            'PASSWORD': row[1]
                        }
                    )
                writer.writerow([row[0],response["AuthenticationResult"]["AccessToken"]])        
                print(f'Generated token for user {row[0]}')

    s3.upload_file(TOKEN_CSV, S3_BUCKET, os.environ['TOKEN_CSV'])

    # disabling ADMIN_NO_SRP_AUTH

    updateUserPool = client.update_user_pool_client(
        UserPoolId = USER_POOL_ID,
        ClientId = CLIENT_ID
    )

except Exception as error:
    print(f'Error - {error}')