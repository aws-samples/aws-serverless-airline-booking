// @ts-nocheck
import { date } from 'quasar'
import Flight from '../../shared/models/FlightClass'
/** Class representing a Booking. All permutations of data from Booking, a different date format for instance, should happen here. */
export default class Booking {
  /**
   *
   * Creates an instance of Booking.
   * @param {Object} Booking
   * @param {string} [Booking.id] - Booking unique ID
   * @param {string} Booking.createdAt - Effective booking was created
   * @param {string} Booking.bookingReference - Booking reference
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
   * let booking = new Booking({
   *    id: "uuid",
   *    createdAt: new Date().toUTCString(),
   *    outboundFlight: new Flight(outbound),
   *    bookingReference: "Flkuc6"
   * });
   */
  constructor({ id, createdAt, outboundFlight, bookingReference }) {
    this.id = id
    this.createdAt = new Date(createdAt)
    this.outboundFlight = new Flight(outboundFlight)
    this.bookingReference = bookingReference
  }
  /**
   * Get the effective booking date
   * @type {string}
   * @readonly
   * @return {string} Formatted booking date (e.g 16 JAN 2019)
   */
  get bookingDate() {
    return date.formatDate(this.createdAt, 'DD MMM YYYY')
  }
}
