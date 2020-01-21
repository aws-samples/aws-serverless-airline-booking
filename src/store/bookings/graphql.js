export const processBookingMutation = `mutation ProcessBooking($input: CreateBookingInput!) {
      processBooking(input: $input) {
        id
      }
    }`

export const listBookingsQuery = `query ListBookings(
      $filter: ModelBookingFilterInput
      $limit: Int
      $nextToken: String
    ) {
      listBookings(filter: $filter, limit: $limit, nextToken: $nextToken) {
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
          }
          createdAt
          bookingReference
        }
        nextToken
      }
    }`
