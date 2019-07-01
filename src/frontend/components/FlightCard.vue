<template>
  <div class="row flight">
    <q-card
      class="flight__card"
      :id="details.flightNumber"
      data-test="flight-card"
    >
      <div class="col-10">
        <q-list highlight>
          <q-list-header>
            <div class="row uppercase text-bold">
              <div class="col">Departure</div>
              <div class="col text-right" data-test="flight-long-date">
                {{ details.departureDayMonthYear }}
              </div>
            </div>
            <div class="row text-primary flight__direction">
              <div class="col flight__left-details">
                <div
                  class="q-headline flight__departure uppercase"
                  data-test="flight-departure-code"
                >
                  {{ details.departureAirportCode }}
                </div>
                <div
                  class="q-caption capitalize text-secondary text-bold"
                  data-test="flight-departure-name"
                >
                  {{ details.departureAirportName }}
                </div>
              </div>
              <div class="col-2 flight__center-details text-center">
                <q-icon class="flight__icon" name="local_airport" />
              </div>
              <div class="col flight__right-details text-right">
                <div
                  class="q-headline flight__arrival uppercase"
                  data-test="flight-arrival-code"
                >
                  {{ details.arrivalAirportCode }}
                </div>
                <div
                  class="q-caption capitalize text-secondary text-bold"
                  data-test="flight-arrival-name"
                >
                  {{ details.arrivalAirportName }}
                </div>
              </div>
            </div>
            <div
              class="row text-primary flight__timing"
              v-if="
                !booking &&
                  details.departureTime &&
                  details.flightDuration &&
                  details.arrivalTime
              "
            >
              <q-card-separator class="flight__separator" />
              <div class="col flight__left-details">
                <div class="row inline">
                  <q-icon class="flight__icon-caption" name="flight_takeoff" />
                  <div
                    class="q-ml-sm q-body-1 text-bold q-pt-xs"
                    data-test="flight-departure-time"
                  >
                    {{ details.departureTime }}
                  </div>
                </div>
              </div>
              <div class="col flight__center-details text-center">
                <div class="row inline">
                  <q-icon class="flight__icon-caption" name="access_time" />
                  <div
                    class="q-ml-sm q-caption text-bold q-pt-xs"
                    data-test="flight-duration"
                  >
                    {{ details.flightDuration }}
                  </div>
                </div>
              </div>
              <div class="col flight__right-details text-right">
                <div class="row inline">
                  <q-icon class="flight__icon-caption" name="flight_land" />
                  <div
                    class="q-ml-sm q-caption text-bold q-pt-xs"
                    data-test="flight-arrival-time"
                  >
                    {{ details.arrivalTime }}
                  </div>
                </div>
              </div>
            </div>
            <div
              class="row flight__ticket"
              v-if="!booking && details.ticketPrice && details.flightNumber"
            >
              <q-card-separator class="flight__separator" />
              <div class="col flight__left-details" v-if="details.ticketPrice">
                <div
                  class="uppercase text-secondary flight__price"
                  data-test="flight-price"
                >
                  {{ details.ticketPrice }} eur
                </div>
              </div>
              <div class="col flight__center-details"></div>
              <div
                class="col flight__right-details text-right"
                v-if="details.flightNumber"
              >
                <div class="row inline">
                  <div class="q-caption text-primary capitalize text-bold">
                    Flight no
                  </div>
                  <div
                    class="q-ml-xs q-caption text-bold"
                    data-test="flight-number"
                  >
                    #{{ details.flightNumber }}
                  </div>
                </div>
              </div>
            </div>
          </q-list-header>
        </q-list>
      </div>
    </q-card>
  </div>
</template>

<script>
import Flight from "../shared/models/FlightClass";
export default {
  /**
   *
   * Flight Card component represents a Flight
   * 
   * @example
   * 
   * // mocked flight data
   * const flight = new Flight({
   *    "id": "173ec46b-0e12-45fe-9ba1-511abde3d318",
   *    "departureDate": "2019-01-16T08:00+0000",
   *    "departureAirportCode": "LGW",
   *    "departureAirportName": "London Gatwick",
   *    "departureCity": "London",
   *    "departureLocale": "Europe/London",
   *    "arrivalDate": "2019-01-16T10:15+0000",
   *    "arrivalAirportCode": "MAD",
   *    "arrivalAirportName": "Madrid Barajas",
   *    "arrivalCity": "Madrid",
   *    "arrivalLocale": "Europe/Madrid",
   *    "ticketPrice": 400,
   *    "ticketCurrency": "EUR",
   *    "flightNumber": 1812
   * })
   * 
   * <flight-card :details="flight"/>
   * 
}
   * 
   */
  name: "FlightCard",
  props: {
    /**
     * @param {Flight} details - Sets Flight details from flight object
     * @param {boolean} booking - Limits amount of information in the card to suit a booking display
     */
    details: { type: Flight, required: true },
    booking: { type: Boolean, default: false }
  }
};
</script>

<style lang="stylus" scoped>
@import '~variables'

.flight
  margin 1.3rem 1rem

.flight__card
  min-width 18rem
  max-width 32rem
  margin auto
  width 100%
  border-radius 0.93rem

.flight__icon
  font-size $item-icon-size

.flight__arrival
  margin-left 2.3rem

.flight__separator
  background-color $secondary
  margin 0.4rem
  width 100%

.flight__icon-caption
  font-size 1.5rem

.flight__price
  font-size 1.3rem

.q-list
  border none
</style>
