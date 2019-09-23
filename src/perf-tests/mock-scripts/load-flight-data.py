import requests
import csv
import os
import json
import boto3

TOKEN_CSV = os.environ['PATH'] + os.environ['TOKEN_CSV']
USER_CSV = os.environ['PATH'] + os.environ['USER_CSV']
APPSYNC_API_KEY = os.environ['APPSYNC_API_KEY']
APPSYNC_API_ENDPOINT_URL = os.environ['GRAPHQL_URL']
S3_BUCKET = os.environ['S3_BUCKET']

s3 = boto3.client('s3')
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
    response = requests.request("POST", APPSYNC_API_ENDPOINT_URL, data=payload, headers=headers)
    return response

if __name__ == '__main__':
    for x in range(9):
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-21T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-22T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-23T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-24T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-25T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-26T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-27T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-28T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-10-29T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))