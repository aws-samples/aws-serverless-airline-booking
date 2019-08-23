/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getLoyalty = `query GetLoyalty($customer: String) {
  getLoyalty(customer: $customer) {
    points
    level
    remainingPoints
  }
}
`;
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
    seatAllocation
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
      seatAllocation
    }
    nextToken
  }
}
`;
export const getBooking = `query GetBooking($id: ID!) {
  getBooking(id: $id) {
    id
    status
    inboundFlight {
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
    }
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
    }
    paymentToken
    checkedIn
    customer
    createdAt
    bookingReference
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
      inboundFlight {
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
      }
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
