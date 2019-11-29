// @ts-nocheck
/**
 * Filters an array of Flights object through departure and/or arrival Date
 * @param {Flight[]} flights - Array of Flight Class to filter on
 * @param {Date} departure - Departure date by filter
 * @param {Date} arrival - Arrival date by filter
 * @returns {Flight[]} flights - Array of Flight Class filtered
 * @example
 * // return flights departing at 8am or later
 * const departure = "2019-04-04T08:00+0000"
 * const filteredFlights = filterBySchedule(flights, { departure })
 * @example
 * // return flights arriving at 11am or later
 * const arrival = "2019-04-04T11:00+0000"
 * const filteredFlights = filterBySchedule(flights, { arrival })
 * @todo - Create a function that takes THIS as an extra arg and calc dates: https://stackoverflow.com/questions/7759237/how-do-i-pass-an-extra-parameter-to-the-callback-function-in-javascript-filter
 */
export const scheduleFilter = {
  methods: {
    filterBySchedule(flights, { departure, arrival }) {
      if (!departure && !arrival) return flights;

      if (departure) {
        flights = flights.filter(function(flight) {
          let flightDatetime = new Date(flight.departureDate);
          let desiredDeparture = new Date(
            flightDatetime.getFullYear(),
            flightDatetime.getMonth(),
            flightDatetime.getDate(),
            departure.getHours(),
            departure.getMinutes()
          );
          let flightSchedule = flightDatetime.getTime();
          let desiredSchedule = desiredDeparture.getTime();
          return flightSchedule >= desiredSchedule;
        });
      }

      if (arrival) {
        flights = flights.filter(function(flight) {
          let flightDatetime = new Date(flight.arrivalDate);
          let desiredArrival = new Date(
            flightDatetime.getFullYear(),
            flightDatetime.getMonth(),
            flightDatetime.getDate(),
            arrival.getHours(),
            arrival.getMinutes()
          );
          let flightSchedule = flightDatetime.getTime();
          let desiredSchedule = desiredArrival.getTime();
          return flightSchedule <= desiredSchedule;
        });
      }

      return flights;
    }
  }
};
