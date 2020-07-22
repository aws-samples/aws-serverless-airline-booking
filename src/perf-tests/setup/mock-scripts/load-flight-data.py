import requests
import csv
import os
import json
import boto3
from datetime import datetime
from datetime import timedelta  

TOKEN_CSV = os.environ['FOLDERPATH'] + os.environ['TOKEN_CSV']
USER_CSV = os.environ['FOLDERPATH'] + os.environ['USER_CSV']
APPSYNC_API_KEY = os.environ['APPSYNC_API_KEY']
APPSYNC_URL = os.environ['APPSYNC_URL']
S3_BUCKET = os.environ['S3_BUCKET']
START_DATE = os.getenv('START_DATE') or datetime.now()
END_DATE = os.getenv('END_DATE') or datetime.now() + timedelta(days=7)

s3 = boto3.client('s3')

try:
    s3.download_file(S3_BUCKET, os.environ['TOKEN_CSV'], TOKEN_CSV)

    with open(TOKEN_CSV, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader, None)
        for row in csv_reader:

            headers = {
                'Content-Type'  : "application/graphql",
                'x-api-key'     : APPSYNC_API_KEY,
                'cache-control' : "no-cache",
                'Authorization' : row[1]
            }
            break

    def execute_gql(query):
        payload_obj = {"query": query}
        print(payload_obj)
        payload = json.dumps(payload_obj)
        response = requests.request("POST", APPSYNC_URL, data=payload, headers=headers)
        return response

    if __name__ == '__main__':
        DATE_TIME_STRING_FORMAT = '%Y-%m-%dT%H:%M+0000'
        while START_DATE <= END_DATE:
            START_DATE = START_DATE + timedelta(hours=1)
            depart_date = datetime.strftime(START_DATE, DATE_TIME_STRING_FORMAT)
            arrival_date = datetime.strftime(START_DATE + timedelta(days=2), DATE_TIME_STRING_FORMAT)
            
            query = f'mutation {{createFlight(input:{{departureDate: "{depart_date}", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: "{arrival_date}", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatCapacity: 2000}}) {{id}}}}'
            print(execute_gql(query)) 

except Exception as error:
    print(f'Exception - {error}')