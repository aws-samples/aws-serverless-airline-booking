// @ts-nocheck
/**
 * Filter flights by ticketPrice property
 * @param {Flight[]} flights - Array of Flight Class to filter on
 * @param {number} maxPrice - Max price a Flight Class ticket should have
 * @returns {Flight[]} flights - Array of Flight Class filtered
 * @example
 * // return flights with less than 500 EUR price tag
 * const filteredFlights = filterByMaxPrice(flights, 500)
 */
export const priceFilter = {
  methods: {
    filterByMaxPrice(flights, maxPrice) {
      if (!maxPrice) return flights;
      return flights.filter(flight => flight.ticketPrice <= maxPrice);
    }
  }
};
