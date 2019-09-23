import boto3
import csv
import os
import json

AWS_REGION = os.environ['AWS_REGION']
client = boto3.client('cognito-idp', region_name=AWS_REGION)
s3 = boto3.client('s3')

TOKEN_CSV = os.environ['PATH'] + os.environ['TOKEN_CSV']
USER_CSV = os.environ['PATH'] + os.environ['USER_CSV']
S3_BUCKET = os.environ['S3_BUCKET']

# START_DATE = os.environ['START_DATE']
# END_DATE = os.environ['END_DATE']

# if sys.argv[1] == "o":
#     user_pool_id = "eu-west-2_Kw4gIJWJf"
# #     client_id = "a7lhrpt7rljvep8bgdccdktjr"
# #     APPSYNC_API_KEY = "ljdossrw5vbivfdvfp37oudll4"
# #     APPSYNC_API_ENDPOINT_URL = "https://ypql3belvjhrbcm2vywgo6usyi.appsync-api.eu-west-2.amazonaws.com/graphql"
# else:
USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['COGNITO_CLIENT_ID']
APPSYNC_API_KEY = os.environ['APPSYNC_API_KEY']
APPSYNC_API_ENDPOINT_URL = os.environ['GRAPHQL_URL']

if os.path.exists(TOKEN_CSV):
    os.remove(TOKEN_CSV)

with open(TOKEN_CSV, mode='a') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    header = ['username', 'token']
    writer.writerow(header)

    print("Reading the user.csv file ...")
    print("------------")
    print("Now generating access tokens...")
    print("------------")

    with open(USER_CSV, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:
            print("=========")
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

print(TOKEN_CSV)
print(os.environ['TOKEN_CSV'])

s3.upload_file(TOKEN_CSV, S3_BUCKET, os.environ['TOKEN_CSV'])