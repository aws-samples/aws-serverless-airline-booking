import requests
import json
import csv
import sys

if sys.argv[1] == "o":
    APPSYNC_API_KEY = "ljdossrw5vbivfdvfp37oudll4"
    APPSYNC_API_ENDPOINT_URL = "https://ypql3belvjhrbcm2vywgo6usyi.appsync-api.eu-west-2.amazonaws.com/graphql"
else:
    APPSYNC_API_KEY = 'cienc2stazc3tgzuemmispbgu4'
    APPSYNC_API_ENDPOINT_URL = 'https://qz6v5gusl5e2xdcevlxrbxtgim.appsync-api.eu-west-2.amazonaws.com/graphql'

with open('/Users/pputhran/Documents/Pawan/Presentations/twitch/gatling/user-files/resources/user-with-token.csv', mode='r') as csv_file:
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
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-08T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-09T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-10T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-11T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-12T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-13T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-14T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-015T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        query = f'mutation {{createFlight(input:{{departureDate: "2019-08-16T0{x}:00+0000", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}}) {{id}}}}'
        print(execute_gql(query))
        ##print(execute_gql("mutation {createFlight(input:{departureDate: \"2019-08-08T00:00+0000\", departureAirportCode: \"LGW\",departureAirportName: \"London Gatwick\",departureCity: \"London\", departureLocale: \"Europe/London\", arrivalDate: \"2019-08-08T03:15+0000\", arrivalAirportCode: \"MAD\", arrivalAirportName: \"Madrid Barajas\", arrivalCity: \"Madrid\", arrivalLocale: \"Europe/Madrid\", ticketPrice: 100, ticketCurrency: \"EUR\",flightNumber: 1830, seatAllocation: 2000}) {id}}").json())


       