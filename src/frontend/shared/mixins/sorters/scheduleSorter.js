/**
 * Sort flights by departureDate property - Earliest to latest departure
 *
 * @param {Flights[]} flights - Array of Flight Class to filter on
 * @returns {Flights[]} flights - Array of Flight Class filtered
 * @example
 * // return flights from earliest to latest departure
 * const filteredFlights = sortByDeparture(flights)
 */
export const scheduleSorter = {
  methods: {
    sortByDeparture(flights) {
      return flights.sort((a, b) => {
        let d1 = new Date(a.departureDate);
        let d2 = new Date(b.departureDate);
        return d1.getTime() - d2.getTime();
      });
    }
  }
};
