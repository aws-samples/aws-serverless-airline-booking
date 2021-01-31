<template>
  <div class="row flight">
    <q-card
      class="flight__card shadow-up-1"
      :id="details.flightNumber"
      data-test="flight-card"
    >
      <div class="col-10">
        <q-list>
          <div class="row text-uppercase text-bold flight__headline">
            <div class="col text-left">Departure</div>
            <div class="col text-right">Arrival</div>
          </div>

          <div class="row text-primary flight__direction items-baseline">
            <div class="col flight__left-details">
              <div
                class="text-h5 flight__departure text-uppercase"
                data-test="flight-departure-time"
              >
                {{ details.departureTime }}
              </div>
            </div>
            <div class="col flight__right-details text-right">
              <div
                class="text-h5 flight__arrival text-uppercase"
                data-test="flight-arrival-time"
              >
                {{ details.arrivalTime }}
              </div>
            </div>
          </div>

          <div
            class="row text-primary flight__timing"
            v-if="
              details.departureTime &&
              details.flightDuration &&
              details.arrivalTime
            "
          >
            <q-separator class="flight__separator" />
            <div class="col flight__left-details">
              <div class="row inline">
                <q-icon class="flight__icon-caption" name="flight_takeoff" />
                <div
                  class="q-ml-sm text-body-1 text-bold q-pt-xs"
                  data-test="flight-departure-code"
                >
                  {{ details.departureAirportCode }}
                </div>
              </div>
            </div>
            <div class="col flight__center-details text-center">
              <div class="row inline">
                <q-icon class="flight__icon-caption" name="access_time" />
                <div
                  class="q-ml-sm text-caption text-bold q-pt-xs"
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
                  class="q-ml-sm text-caption text-bold q-pt-xs"
                  data-test="flight-arrival-code"
                >
                  {{ details.arrivalAirportCode }}
                </div>
              </div>
            </div>
          </div>

          <div
            class="row flight__ticket items-baseline"
            v-if="!booking && details.ticketPrice && details.flightNumber"
          >
            <q-separator class="flight__separator" />
            <div
              class="col flight__left-details text-grey-9"
              v-if="details.ticketPrice"
            >
              <div
                class="text-uppercase text-grey-9 flight__price"
                data-test="flight-price"
              >
                <span>&euro; {{ details.ticketPrice }}</span>
              </div>
            </div>
            <div class="col flight__center-details"></div>
            <div
              class="col flight__right-details text-right"
              v-if="details.flightNumber"
            >
              <div class="row inline text-grey-9">
                <div class="text-caption capitalize text-bold">Flight</div>
                <div
                  class="q-ml-xs text-caption text-bold"
                  data-test="flight-number"
                >
                  {{ details.flightNumber }}
                </div>
              </div>
            </div>
          </div>
        </q-list>
      </div>
    </q-card>
  </div>
</template>

<script>
import Flight from '../shared/models/FlightClass'
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
  name: 'FlightCard',
  props: {
    /**
     * @param {Flight} details - Sets Flight details from flight object
     * @param {boolean} booking - Limits amount of information in the card to suit a booking display
     */
    details: { type: Flight, required: true },
    booking: { type: Boolean, default: false }
  }
}
</script>

<style lang="sass" scoped>
@import '../css/app'

.flight
  margin: 1.3rem 1rem

.flight__card
  min-width: 18rem
  max-width: 25rem
  margin: auto
  width: 100%
  &::after
    content: ''
    position: absolute
    top: 0
    bottom: 0
    left: 0
    right: 0
    opacity: 0
    box-shadow: 0 5px 15px rgba(0,0,0,0.3)
    transition: opacity 1s ease
  &:hover::after
    opacity: 1
    border-bottom: 1.5px solid $secondary

.flight__icon
  font-size: $item-icon-size

.flight__arrival
  margin-left: 2.3rem

.flight__separator
  background-color: $grey-3
  margin: 0.4rem
  width: 100%

.flight__icon-caption
  font-size: 1.5rem

.flight__price
  font-size: 1rem

.q-list
  border: none
  color: #757575
  font-size: 14px
  font-weight: 500
  line-height: 18px
  min-height: 48px
  padding: 15px 16px

.flight__headline
  color: #757575
  font-size: 0.8rem
</style>
