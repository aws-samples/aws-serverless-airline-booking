<template>
  <q-modal ref="modal" content-classes="booking__modal">
    <q-toolbar color="primary">
      <q-btn flat round dense v-close-overlay icon="close" />
      <q-toolbar-title class="booking__modal--title self-center">
        <div class="row q-pt-md">
          <p
            class="no-margin booking__departure--code"
            data-test="booking-departure-code"
          >
            {{ departureIata }}
          </p>
          <q-icon name="keyboard_arrow_right" size="1.3rem" />
          <p class="booking__arrival--code" data-test="booking-arrival-code">
            {{ arrivalIata }}
          </p>
        </div>
      </q-toolbar-title>
    </q-toolbar>
    <div
      class="booking__modal--passenger booking__modal--highlighted text-center q-pa-md"
    >
      <div class="q-headline text-primary q-mb-sm" data-test="booking-customer">
        {{ name }}
      </div>
      <div class="q-body-2">
        Booking reference:
        <span class="text-primary" data-test="booking-reference">{{
          reference
        }}</span>
      </div>
    </div>
    <div class="row">
      <q-timeline responsive color="secondary" style="padding: 0 24px;">
        <q-timeline-entry
          :subtitle="departureDisplayDate"
          icon="flight_takeoff"
        >
          <q-list highlight no-border class="q-pa-none">
            <q-item class="q-pa-none">
              <q-item-main
                class="text-bold"
                :label="departureTime"
                data-test="booking-departure-time"
              />
              <q-item-main
                :label="departureAirportName"
                data-test="booking-departure-code"
              />
            </q-item>
          </q-list>
        </q-timeline-entry>

        <q-timeline-entry :subtitle="arrivalDisplayDate" icon="flight_land">
          <q-list highlight no-border class="q-pa-none">
            <q-item class="q-pa-none">
              <q-item-main
                class="text-bold"
                :label="arrivalTime"
                data-test="booking-arrival-time"
              />
              <q-item-main
                :label="arrivalAirportName"
                data-test="booking-arrival-code"
              />
            </q-item>
          </q-list>
        </q-timeline-entry>
      </q-timeline>

      <div
        class="booking__modal--ctas booking__modal--highlighted row inline full-width q-pl-lg"
      >
        <div class="col-6">
          <q-btn
            class="full-width cta__button-check-in"
            flat
            color="primary"
            label="Check-in"
            data-test="booking-check-in"
            @click="checkIn"
          />
        </div>
        <div class="col-6">
          <q-btn
            class="full-width cta__button-cancel"
            flat
            color="secondary"
            label="Cancel booking"
            data-test="booking-cancel"
            @click="cancelBooking"
          />
        </div>
      </div>
    </div>
  </q-modal>
</template>
<style lang="stylus">
@import '~variables'

.booking__modal
  &--title
    margin 0 auto

  &--highlighted
    background $grey-1

  .q-timeline-content
    padding 0

  .q-item
    min-height none

  h6
    margin 0
    padding 0
</style>
<script>
// @ts-ignore
import { date } from "quasar";

export default {
  /**
   *
   * Booking Card component represents booking details
   * It uses data from both Flight and Booking for rendering
   */
  name: "BookingCard",
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
    departureDate: [String, Date],
    departureAirportName: String,
    departureIata: {
      type: String,
      validator: function(value) {
        return value.length == 3;
      }
    },
    arrivalDate: [String, Date],
    arrivalAirportName: String,
    arrivalIata: {
      type: String,
      validator: function(value) {
        return value.length == 3;
      }
    }
  },
  methods: {
    /**
     * Display modal
     *
     * @see BookingFlight
     */
    showCard: function() {
      // @ts-ignore
      this.$refs["modal"].show();
    },
    /**
     * Hides modal
     *
     * @see BookingFlight
     */
    hideCard: function() {
      // @ts-ignore
      this.$refs["modal"].hide();
    },
    checkIn() {
      this.$q.notify("Not implemented");
    },
    cancelBooking() {
      this.$q.notify("Not implemented");
    }
  },
  /**
   *
   * At mount lifecycle hook, it formats departure/arrival dates to be displayed
   *
   */
  mounted() {
    this.departureDisplayDate = date.formatDate(
      // @ts-ignore
      this.departureDate,
      "ddd, DD MMM YYYY"
    );
    // @ts-ignore
    this.departureTime = date.formatDate(this.departureDate, "HH:mm");

    this.arrivalDisplayDate = date.formatDate(
      // @ts-ignore
      this.departureDate,
      "ddd, DD MMM YYYY"
    );
    // @ts-ignore
    this.arrivalTime = date.formatDate(this.arrivalDate, "HH:mm");
  },
  data() {
    return {
      departureTime: null,
      departureDisplayDate: null,
      arrivalTime: null,
      arrivalDisplayDate: null
    };
  }
};
</script>
