export const processBooking = `mutation ProcessBooking($input: CreateBookingInput!) {
  processBooking(input: $input) {
    id
  }
}
`;

export const getBookingByStatus = `query GetBookingByStatus(
  $customer: String
  $statusCreatedAt: ModelBookingByStatusCompositeKeyConditionInput
  $sortDirection: ModelSortDirection
  $filter: ModelBookingFilterInput
  $limit: Int
  $nextToken: String
) {
  getBookingByStatus(
    customer: $customer
    statusCreatedAt: $statusCreatedAt
    sortDirection: $sortDirection
    filter: $filter
    limit: $limit
    nextToken: $nextToken
  ) {
    items {
      id
      status
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
        seatAllocation
        seatCapacity
      }
      paymentToken
      checkedIn
      customer
      createdAt
      bookingReference
    }
    nextToken
  }
}
`;
