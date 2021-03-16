<template>
  <q-page>
    <div class="wrapper">
      <div
        class="text-h4 text-primary booking__heading"
        data-test="booking-headline"
      >
        Bookings
      </div>
    </div>
    <div class="bookings q-mt-xl">
      <h5 class="text-center" v-if="!bookings || !bookings.length">
        No bookings available
      </h5>
      <q-timeline color="secondary" class="q-pl-md" v-else>
        <div class="booking" v-for="booking in bookings" :key="booking.id">
          <q-timeline-entry
            :subtitle="bookingDestination(booking)"
            class="booking__entry"
            icon="flight_takeoff"
            side="left"
            color="primary"
          >
            <booking-flight
              :bookingID="booking.bookingReference"
              :flight="booking.outboundFlight"
            />
          </q-timeline-entry>
        </div>
      </q-timeline>
      <div class="wrapper">
        <q-btn
          v-if="paginationToken"
          @click="loadBookings"
          class="cta__button"
          color="secondary"
          size="1rem"
          label="Load more bookings?"
          data-test="booking-pagination"
        />
      </div>
    </div>
    <q-page-scroller
      expand
      position="bottom-right"
      :scroll-offset="150"
      :offset="[18, 18]"
    >
      <q-btn fab-mini icon="keyboard_arrow_up" color="accent" />
    </q-page-scroller>
  </q-page>
</template>

<script>
// @ts-nocheck
import BookingFlight from '../components/BookingFlight'
import { mapState, mapGetters } from 'vuex'
import { Logger } from '@aws-amplify/core'

const logger = new Logger('Bookings')

/**
 * Booking view displays bookings from authenticated customer.
 * It uses `BookingFlight` component to render bookings once fetched
 */
export default {
  name: 'Bookings',
  components: {
    BookingFlight
  },
  mounted() {
    /** authentication guards prevent authenticated users to view Bookings
     * however, the component doesn't stop from rendering asynchronously
     * this guarantees we attempt talking to Booking service
     * if our authentication guards && profile module have an user in place
     */
    if (this.isAuthenticated) {
      this.loadBookings()
    }
  },
  methods: {
    /**
     * loadBookings method fetches all bookings via booking API
     */
    async loadBookings() {
      try {
        await this.$store.dispatch(
          'bookings/fetchBooking',
          this.paginationToken
        )
      } catch (error) {
        logger.error('Error while fetching bookings: ', error)
        this.$q.notify(
          `Unable to fetch bookings - Check browser console messages`
        )
      }
    },
    bookingDestination(booking) {
      const departure = booking.outboundFlight?.departureCity ?? 'Departure'
      const arrival = booking.outboundFlight?.arrivalCity ?? 'Arrival'
      const date = booking.bookingDate ?? ''
      return `${departure}-${arrival} - ${date}`
    }
  },
  /**
   * @param {Booking} bookings - Bookings state from Bookings module
   * @param {boolean} isAuthenticated - Getter from Profile module
   */
  computed: {
    ...mapState({
      bookings: (state) => state.bookings.bookings,
      paginationToken: (state) => state.bookings.paginationToken
    }),
    ...mapGetters('profile', ['isAuthenticated'])
  }
}
</script>
<style lang="sass">
@import '../css/app'

.booking__heading
  margin-top: 2rem

.booking__flight
  margin: 0 !important
  margin-right: 1rem !important

.booking__entry
  padding-left: 2rem

.q-timeline__subtitle
  body.screen--lg &
    font-size: 1rem !important

.flight
  margin-right: 5vw !important
  margin-left: 0 !important

  &__card
    max-width: 25rem !important

.q-timeline__subtitle
  opacity: 0.7 !important
</style>
