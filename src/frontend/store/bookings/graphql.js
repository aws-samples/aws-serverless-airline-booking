export const processBooking = `mutation ProcessBooking($input: CreateBookingInput!) {
  processBooking(input: $input) {
    id
  }
}
`;

export const listBookings = `query ListBookings(
  $filter: ModelBookingFilterInput
  $limit: Int
  $nextToken: String
) {
  listBookings(filter: $filter, limit: $limit, nextToken: $nextToken) {
    items {
      id
      status
      bookingReference
      outboundFlight {
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
      checkedIn
      createdAt
    }
    nextToken
  }
}
`;
