<template>
  <div @click="toggle" class="booking_flights">
    <div class="booking_flight">
      <flight-card :details="flight" booking />
    </div>
    <BookingCard
      ref="card"
      :reference="bookingID"
      :name="fullName"
      :flightNumber="flight.flightNumber"
      :departureDate="flight.departureDate"
      :departureAirportName="flight.departureAirportName"
      :departureIata="flight.departureAirportCode"
      :arrivalDate="flight.arrivalDate"
      :arrivalAirportName="flight.arrivalAirportName"
      :arrivalIata="flight.arrivalAirportCode"
    />
  </div>
</template>

<script>
// @ts-ignore
import FlightCard from './FlightCard'
// @ts-ignore
import BookingCard from './BookingCard'

import { mapState, mapGetters } from 'vuex'

export default {
  /**
   *
   * Booking Flight component represents a booked flight alongside with its details for Check-in/Cancellation
   * It uses FlightCard component to render a minimized Flight Card version
   * It uses BookingCard component to render booking details
   *
   * @example
   *
   * const flight = new Flight(flightData)
   *
   * <booking-flight
   * :bookingID="bookingID"
   * :flight="flight"
   * />
   *
   */
  name: 'BookingFlight',

  components: {
    BookingCard,
    FlightCard
  },
  computed: {
    ...mapState({
      user: (state) => state.profile.user
    }),
    ...mapGetters({
      firstName: 'profile/firstName',
      lastName: 'profile/lastName'
    }),
    fullName() {
      return `${this.firstName} ${this.lastName}`
    }
  },
  props: {
    /**
     * @param {string} bookingID - Sets Booking ID
     * @param {Flight} flight - Sets Booking Flight details from flight object
     */
    bookingID: String,
    flight: Object
  },
  methods: {
    /**
     * Gets called when the user clicks on the booking card for more details
     *
     * @see BookingCard
     * @see Bookings
     */

    toggle: function () {
      // @ts-ignore
      this.$refs['card'].showCard()
    }
  }
}
</script>

<style lang="sass" scoped>
@import '../css/app'

.booking_flight
  &:hover
    cursor: pointer
</style>
