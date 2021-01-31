/**
 * Sort flights by departureDate property - Earliest to latest departure
 *
 * @param {Flights[]} flights - Flights to be sorted
 * @returns {Flights[]} flights - Flights sorted
 * @example
 * // return flights from earliest to latest departure
 * const filteredFlights = sortByEarliestDeparture(flights)
 */
export const sortByEarliestDeparture = (flights) => {
  return flights.sort((a, b) => {
    const departureA = new Date(a.departureDate)
    const departureB = new Date(b.departureDate)
    return departureA.getTime() - departureB.getTime()
  })
}

/**
 * Sort flights by departureDate property - Latest to earliest departure
 *
 * @param {Flights[]} flights - Flights to be sorted
 * @returns {Flights[]} flights - Flights sorted
 * @example
 * // return flights from earliest to latest departure
 * const filteredFlights = sortByLatestDeparture(flights)
 */
export const sortByLatestDeparture = (flights) => {
  return flights.sort((a, b) => {
    const departureA = new Date(a.departureDate)
    const departureB = new Date(b.departureDate)
    return departureB.getTime() - departureA.getTime()
  })
}
