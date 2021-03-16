/**
 * Sort flights by ticketPrice property - Least to most expensive
 *
 * @param {Flights[]} flights - Flights to be sorted
 * @returns {Flights[]} flights - Flights sorted
 * @example
 * // return flights sorted from least to most expensive
 * const filteredFlights = sortByLowestPrice(flights)
 */
export const sortByLowestPrice = (flights) => {
  return flights.sort((a, b) => a.ticketPrice - b.ticketPrice)
}

/**
 * Sort flights by ticketPrice property - Highest to least expensive
 *
 * @param {Flights[]} flights - Flights to be sorted
 * @returns {Flights[]} flights - Flights sorted
 * @example
 * // return flights sorted from least to most expensive
 * const filteredFlights = sortByHighestPrice(flights)
 */
export const sortByHighestPrice = (flights) => {
  return flights.sort((a, b) => b.ticketPrice - a.ticketPrice)
}
