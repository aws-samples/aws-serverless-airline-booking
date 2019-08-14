/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getFlight = `query GetFlight($id: ID!) {
  getFlight(id: $id) {
    id
    departureDate
    departureAirportCode
    departureAirportName
    departureCity
    departureLocale
    arrivalDate
    arrivalAirportCode
    arrivalAirportName
    arrivalCity
    arrivalLocale
    ticketPrice
    ticketCurrency
    flightNumber
  }
}
`;
export const listFlights = `query ListFlights(
  $filter: ModelFlightFilterInput
  $limit: Int
  $nextToken: String
) {
  listFlights(filter: $filter, limit: $limit, nextToken: $nextToken) {
    items {
      id
      departureDate
      departureAirportCode
      departureAirportName
      departureCity
      departureLocale
      arrivalDate
      arrivalAirportCode
      arrivalAirportName
      arrivalCity
      arrivalLocale
      ticketPrice
      ticketCurrency
      flightNumber
    }
    nextToken
  }
}
`;
