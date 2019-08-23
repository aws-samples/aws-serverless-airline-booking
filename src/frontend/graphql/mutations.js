/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const processBooking = `mutation ProcessBooking($input: CreateBookingInput!) {
  processBooking(input: $input) {
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
export const createFlight = `mutation CreateFlight($input: CreateFlightInput!) {
  createFlight(input: $input) {
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
export const updateFlight = `mutation UpdateFlight($input: UpdateFlightInput!) {
  updateFlight(input: $input) {
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
export const deleteFlight = `mutation DeleteFlight($input: DeleteFlightInput!) {
  deleteFlight(input: $input) {
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
export const createBooking = `mutation CreateBooking($input: CreateBookingInput!) {
  createBooking(input: $input) {
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
export const updateBooking = `mutation UpdateBooking($input: UpdateBookingInput!) {
  updateBooking(input: $input) {
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
export const deleteBooking = `mutation DeleteBooking($input: DeleteBookingInput!) {
  deleteBooking(input: $input) {
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
