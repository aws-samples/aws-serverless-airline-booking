<template>
  <q-page>
    <div class="wrapper">
      <div class="q-display-1 text-primary booking__heading">Bookings</div>
    </div>
    <div class="bookings">
      <q-timeline color="secondary" class="q-pl-md">
        <div class="booking" v-for="booking in bookings" :key="booking.id">
          <q-timeline-entry
            class="booking__entry"
            icon="flight_takeoff"
            side="left"
          >
            <h5 slot="subtitle" class="q-timeline-subtitle">
              <span>
                {{ booking.departureCity }} &mdash; {{ booking.bookingDate }}
              </span>
            </h5>
            <booking-flight
              :bookingID="booking.id"
              :flight="booking.outboundFlight"
            />
            <booking-flight
              :bookingID="booking.id"
              :flight="booking.inboundFlight"
            />
          </q-timeline-entry>
        </div>
      </q-timeline>
    </div>
  </q-page>
</template>

<script>
// @ts-nocheck
import BookingFlight from "../components/BookingFlight";
import { mapState, mapGetters } from "vuex";

/**
 * Booking view displays bookings from authenticated customer.
 * It uses `BookingFlight` component to render bookings once fetched
 */
export default {
  name: "Bookings",
  components: {
    BookingFlight
  },
  async mounted() {
    /** authentication guards prevent authenticated users to view Bookings
     * however, the component doesn't stop from rendering asynchronously
     * this guarantees we attempt talking to Booking service
     * if our authentication guards && profile module have an user in place
     */
    if (this.isAuthenticated) {
      await this.$store.dispatch("bookings/fetchBooking");
    }
  },
  /**
   * @param {Booking} bookings - Bookings state from Bookings module
   * @param {boolean} isAuthenticated - Getter from Profile module
   */
  computed: {
    ...mapState({
      bookings: state => state.bookings.bookings
    }),
    ...mapGetters("profile", ["isAuthenticated"])
  }
};
</script>
<style lang="stylus">
@import '~variables'

.booking__heading
  margin-top 2rem

.booking__flight
  margin 0 !important
  margin-right 1rem !important

.booking__entry
  padding-left 2rem
</style>
