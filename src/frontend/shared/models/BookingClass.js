// @ts-nocheck
import { date } from "quasar";

/** Class representing a Booking. All permutations of data from Booking, a different date format for instance, should happen here. */
export default class Booking {
  /**
   *
   * Creates an instance of Booking.
   * @param {Object} Booking
   * @param {string} [Booking.id] - Booking ID
   * @param {string} Booking.departureCity - Booking Departure City
   * @param {string} Booking.transactionDate - Effective booking was created
   * @param {Flight} Booking.inboundFlight - Inbound flight
   * @param {Flight} Booking.outboundFlight - Outbound flight
   *
   * @todo Move to TS and create a Flight Interface
   * @example
   * let outbound = {
   *    id: "173ec46b-0e12-45fe-9ba1-511abde3d318",
   *    departureDate: "2019-01-16T08:00+0000",
   *    departureAirportCode: "LGW",
   *    departureAirportName: "London Gatwick",
   *    departureCity: "London",
   *    departureLocale: "Europe/London",
   *    arrivalDate: "2019-01-16T10:15+0000",
   *    arrivalAirportCode: "MAD",
   *    arrivalAirportName: "Madrid Barajas",
   *    arrivalCity: "Madrid",
   *    arrivalLocale: "Europe/Madrid",
   *    ticketPrice: 400,
   *    ticketCurrency: "EUR",
   *    flightNumber: 1812
   * };
   *
   * let inbound = {
   *    id: "f976e763-5e43-45d0-83b2-8190698b2cdc",
   *    departureDate: "2019-01-17T08:00+0000",
   *    departureAirportCode: "MAD",
   *    departureAirportName: "Madrid Barajas",
   *    departureCity: "Madrid",
   *    departureLocale: "Europe/Madrid",
   *    arrivalDate: "2019-01-16T10:15+0000",
   *    arrivalAirportCode: "LGW",
   *    arrivalAirportName: "London Gatwick",
   *    arrivalCity: "London",
   *    arrivalLocale: "Europe/London",
   *    ticketPrice: 400,
   *    ticketCurrency: "EUR",
   *    flightNumber: 1813
   * };
   *
   * let booking = new Booking({
   *    id: "FJ9KLW",
   *    departureCity: outbound.departureCity,
   *    transactionDate: new Date().toUTCString(),
   *    inboundFlight: new Flight(inbound),
   *    outboundFlight: new Flight(outbound)
   * });
   */
  constructor({
    id,
    departureCity,
    transactionDate,
    inboundFlight,
    outboundFlight
  }) {
    this.id = id;
    this.departureCity = departureCity;
    this.transactionDate = new Date(transactionDate);
    this.inboundFlight = inboundFlight;
    this.outboundFlight = outboundFlight;
  }
  /**
   * Get the effective booking date
   * @type {string}
   * @readonly
   * @return {string} Formatted booking date (e.g 16 JAN 2019)
   */
  get bookingDate() {
    return date.formatDate(this.transactionDate, "DD MMM YYYY");
  }
}
