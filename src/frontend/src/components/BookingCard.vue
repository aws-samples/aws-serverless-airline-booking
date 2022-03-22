<template>
  <q-dialog ref="modal">
    <div class="row booking__modal">
      <div
        class="
          col-12
          booking__modal--passenger booking__modal--highlighted
          text-center
          q-pa-sm
          bg-grey-3
        "
      >
        <q-list separator>
          <q-item
            dense
            class="booking__modal--header no-padding items-baseline"
          >
            <q-item-section>
              <q-item-label
                overline
                class="text-uppercase text-primary text-bold"
                >Flight</q-item-label
              >
              <q-item-label class="text-subtitle1 text-bold">{{
                flightNumber
              }}</q-item-label>
            </q-item-section>
            <q-item-section>
              <q-item-label
                overline
                class="text-uppercase text-primary text-bold"
                >Reference</q-item-label
              >
              <q-item-label class="text-uppercase text-subtitle1 text-bold">{{
                reference
              }}</q-item-label>
            </q-item-section>
            <q-item-section>
              <q-item-label
                overline
                class="text-uppercase text-primary text-bold"
                >Boarding</q-item-label
              >
              <q-item-label class="text-subtitle1 text-bold">{{
                boardingTime
              }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <div class="row booking__modal--timeline full-width">
        <q-timeline responsive color="primary" layout="loose">
          <q-timeline-entry
            :subtitle="departureDisplayDate"
            icon="flight_takeoff"
            side="right"
            :title="departureAirportName"
          >
          </q-timeline-entry>

          <q-timeline-entry
            :subtitle="arrivalDisplayDate"
            icon="flight_land"
            :title="arrivalAirportName"
          >
          </q-timeline-entry>
        </q-timeline>
      </div>

      <div
        class="
          booking__modal--ctas booking__modal--highlighted
          row
          inline
          full-width
          bg-grey-1
        "
      >
        <div class="col-12 bg-primary">
          <q-btn
            class="full-width cta__button-check-in text-bold"
            flat
            color="white"
            label="Check-in"
            data-test="booking-check-in"
            @click="checkIn"
          />
        </div>
        <div class="col-12">
          <q-btn
            class="full-width cta__button-cancel text-bold"
            flat
            label="Cancel"
            data-test="booking-cancel"
            @click="cancelBooking"
          />
        </div>
      </div>
    </div>
  </q-dialog>
</template>
<style lang="sass">
@import '../css/app'

.booking__modal

  &--title
    margin: 0 auto

  &--timeline
    background-color: white
    padding: 0 0.1rem


.q-timeline__title
  font-size: 1rem !important
  margin-bottom: 1vh !important

.booking__timeline--info
  body.screen--lg &
    font-size: 1rem !important
</style>
<script>
// @ts-ignore
import { date } from 'quasar'

export default {
  /**
   *
   * Booking Card component represents booking details
   * It uses data from both Flight and Booking for rendering
   */
  name: 'BookingCard',
  props: {
    /**
     * @param {string} reference - Sets Booking ID
     * @param {string} name - Passenger name
     * @param {string} departureDate - Departure date
     * @param {string} departureAirportName - Departure airport known name
     * @param {string} departureIata - Departure airport code
     * @param {string} arrivalDate - Arrival date
     * @param {string} arrivalIata - Arrival airport code
     */
    reference: String,
    name: String,
    flightNumber: Number,
    departureDate: [String, Date],
    departureAirportName: String,
    departureIata: {
      type: String,
      validator: function (value) {
        return value.length == 3
      }
    },
    arrivalDate: [String, Date],
    arrivalAirportName: String,
    arrivalIata: {
      type: String,
      validator: function (value) {
        return value.length == 3
      }
    }
  },
  methods: {
    /**
     * Display modal
     *
     * @see BookingFlight
     */
    showCard: function () {
      // @ts-ignore
      this.$refs['modal'].show()
    },
    checkIn() {
      this.$q.notify('Not implemented')
    },
    cancelBooking() {
      this.$q.notify('Not implemented')
    }
  },
  computed: {
    boardingTime() {
      let boarding = date.subtractFromDate(this.departureDate, { minutes: 45 })
      return date.formatDate(boarding, 'HH:mm')
    },
    arrivalTime() {
      return date.formatDate(this.arrivalDate, 'HH:mm')
    },
    departureTime() {
      return date.formatDate(this.departureDate, 'HH:mm')
    },
    departureDisplayDate() {
      return date.formatDate(this.departureDate, 'ddd, DD MMM YYYY')
    },
    arrivalDisplayDate() {
      return date.formatDate(this.arrivalDate, 'ddd, DD MMM YYYY')
    }
  }
}
</script>
