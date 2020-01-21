export const getFlightQuery = `query GetFlight($id: ID!) {
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
    }`

export const listFlightQuery = `query listFlights($filter: ModelFlightFilterInput) {
      listFlights(filter: $filter) {
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
      }
    }`
