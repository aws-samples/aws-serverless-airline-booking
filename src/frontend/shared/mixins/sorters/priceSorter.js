/**
 * Sort flights by ticketPrice property - Least to most expensive
 *
 * @param {Flights[]} flights - Array of Flight Class to sort on
 * @returns {Flights[]} flights - Array of Flight Class sorted
 * @example
 * // return flights sorted from least to most expensive
 * const filteredFlights = sortByPrice(flights)
 */
export const priceSorter = {
  methods: {
    sortByPrice(flights) {
      return flights.sort((a, b) => a.ticketPrice - b.ticketPrice);
    }
  }
};
