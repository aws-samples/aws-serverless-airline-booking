export const getFlightBySchedule = `query GetFlightBySchedule(
  $departureAirportCode: String
  $arrivalAirportCodeDepartureDate: ModelFlightByDepartureScheduleCompositeKeyConditionInput
  $sortDirection: ModelSortDirection
  $filter: ModelFlightFilterInput
  $limit: Int
  $nextToken: String
) {
  getFlightBySchedule(
    departureAirportCode: $departureAirportCode
    arrivalAirportCodeDepartureDate: $arrivalAirportCodeDepartureDate
    sortDirection: $sortDirection
    filter: $filter
    limit: $limit
    nextToken: $nextToken
  ) {
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
      seatCapacity
    }
    nextToken
  }
}
`

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
`
