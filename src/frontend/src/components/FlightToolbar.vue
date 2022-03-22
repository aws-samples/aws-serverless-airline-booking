<template>
  <div class="bg-grey-2">
    <div
      class="
        flight__toolbar
        container
        row
        text-left
        justify-around
        items-baseline
        text-subtitle1
      "
    >
      <div class="flight__filters--departure col">
        <q-select
          v-model="departureCity"
          class="flight__departure--toolbar no-padding"
          label="From"
          borderless
          dense
          use-input
          item-aligned
          hide-selected
          hide-dropdown-icon
          hide-hint
          fill-input
          hide-bottom-space
          input-class="search__options--input"
          :disable="this.$router.currentRoute.name != 'searchResults'"
          :min-characters="3"
          :options="$data.airportSearch_suggestionList"
          option-label="code"
          option-value="code"
          options-dense
          emit-value
          input-debounce="200"
          @filter="$airportSearch_fuzzySearch"
          @input="updateDestination"
          display-value-sanitize
          behavior="dialog"
        >
          <span class="search__options--editable"></span>
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps" v-on="scope.itemEvents">
              <q-item-section avatar>
                <q-icon name="local_airport" />
              </q-item-section>
              <q-item-section>
                <q-item-label v-html="scope.opt.label" />
                <q-item-label class="text-subtitle1 search__options--suggestion"
                  >{{ scope.opt.name }} ({{ scope.opt.code }})</q-item-label
                >
              </q-item-section>
            </q-item>
          </template>
        </q-select>
      </div>
      <div class="flight__filters--arrival col">
        <q-select
          v-model="arrivalCity"
          class="flight__arrival--toolbar no-padding"
          label="To"
          borderless
          dense
          use-input
          item-aligned
          hide-selected
          hide-dropdown-icon
          hide-hint
          fill-input
          hide-bottom-space
          input-class="search__options--input"
          :disable="this.$router.currentRoute.name != 'searchResults'"
          :min-characters="3"
          :options="$data.airportSearch_suggestionList"
          option-label="code"
          option-value="code"
          map-options
          emit-value
          input-debounce="200"
          @filter="$airportSearch_fuzzySearch"
          @input="updateDestination"
          display-value-sanitize
          behavior="dialog"
        >
          <span class="search__options--editable"></span>
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps" v-on="scope.itemEvents">
              <q-item-section avatar>
                <q-icon name="local_airport" />
              </q-item-section>
              <q-item-section>
                <q-item-label v-html="scope.opt.label" />
                <q-item-label class="text-subtitle1 search__options--suggestion"
                  >{{ scope.opt.name }} ({{ scope.opt.code }})</q-item-label
                >
              </q-item-section>
            </q-item>
          </template>
        </q-select>
      </div>
      <div class="flight__filters--date col-4">
        <q-field
          class="text-bold flight__departure--date cursor-pointer"
          borderless
          label="Date"
          stack-label
          hide-bottom-space
          :disable="this.$router.currentRoute.name != 'searchResults'"
        >
          <template v-slot:control>
            <q-popup-proxy>
              <div>
                <q-date
                  v-model="departureDate"
                  mask="YYYY-MM-DD"
                  today-btn
                  @input="updateDestination"
                />
              </div>
            </q-popup-proxy>
            <span class="text-primary text-bold search__options--date">{{
              shortDate
            }}</span>
          </template>
        </q-field>
      </div>
      <div class="flight__filters--filter">
        <q-field
          borderless
          label="Refine"
          label-color="grey-6.5"
          stack-label
          hide-bottom-space
          :disable="this.$router.currentRoute.name != 'searchResults'"
        >
          <template v-slot:control>
            <div>
              <q-btn
                class="text-bold"
                dense
                flat
                text-color="primary"
                size="0.75rem"
                label="Filter"
                padding="0"
                @click="toggleFilters"
              >
              </q-btn>
              <span> | </span>
              <q-btn-dropdown
                class="text-bold"
                flat
                text-color="primary"
                size="0.75rem"
                label="Sort"
                padding="0"
                auto-close
              >
                <q-list separator>
                  <q-item
                    clickable
                    @click="sortResults(SortPreference.LowestPrice)"
                    :active="sortSelection == SortPreference.LowestPrice"
                    active-class="bg-cyan-2 text-dark"
                  >
                    <q-item-section>
                      <q-item-label class="text-subtitle1"
                        >Lowest price</q-item-label
                      >
                      <q-item-label caption
                        >Lowest to highest ticket price</q-item-label
                      >
                    </q-item-section>
                  </q-item>

                  <q-item
                    clickable
                    @click="sortResults(SortPreference.HighestPrice)"
                    :active="sortSelection == SortPreference.HighestPrice"
                    active-class="bg-cyan-2 text-dark"
                  >
                    <q-item-section>
                      <q-item-label class="text-subtitle1"
                        >Highest price</q-item-label
                      >
                      <q-item-label caption
                        >Highest to lowest ticket price</q-item-label
                      >
                    </q-item-section>
                  </q-item>

                  <q-item
                    clickable
                    @click="sortResults(SortPreference.EarliestDeparture)"
                    :active="sortSelection == SortPreference.EarliestDeparture"
                    active-class="bg-cyan-2 text-dark"
                  >
                    <q-item-section>
                      <q-item-label class="text-subtitle1"
                        >Earliest departure</q-item-label
                      >
                      <q-item-label caption
                        >Earliest to latest departure time
                      </q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item
                    clickable
                    @click="sortResults(SortPreference.LatestDeparture)"
                    :active="sortSelection == SortPreference.LatestDeparture"
                    active-class="bg-cyan-2 text-dark"
                  >
                    <q-item-section>
                      <q-item-label class="text-subtitle1"
                        >Latest departure</q-item-label
                      >
                      <q-item-label caption
                        >Latest to earliest departure time</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <flight-toolbar-filters ref="filters" @apply="applyFilters" />
            </div>
          </template>
        </q-field>
      </div>
    </div>
  </div>
</template>

<script>
import { date } from 'quasar'
import FlightToolbarFilters from './FlightToolbarFilters.vue'
import { SortPreference } from '../shared/enums'
import { airportSearchMixin } from '../shared/mixins/'
import { Logger } from '@aws-amplify/core'

const logger = new Logger('Toolbar')

export default {
  /**
   *
   * Flight Toolbar component represents flight direction when searching/paying for a given flight
   *
   * @example
   *
   * <flight-toolbar />
   */
  name: 'FlightToolbar',
  mixins: [airportSearchMixin],
  components: {
    FlightToolbarFilters
  },
  data() {
    return {
      sortSelection: '',
      SortPreference,
      /**
       * @param {string} departureCity - Departure city IATA airport code
       * @param {string} arrivalCity - Arrival city IATA airport code
       * @param {string} departureDate - Departure date (e.g. 2021-01-30)
       */
      departureCity: this.$router.currentRoute.query.departure,
      arrivalCity: this.$router.currentRoute.query.arrival,
      departureDate: this.$router.currentRoute.query.date
    }
  },
  computed: {
    shortDate() {
      return date.formatDate(this.departureDate, 'ddd, DD MMM')
    }
  },
  methods: {
    /**
     * Apply flight filters
     *
     * @param {object} obj - Object containing flight filters
     * @param {object} obj.pricing - Price filters
     * @param {number} obj.pricing.min - Minimum flight ticket price
     * @param {number} obj.pricing.max - Maximum flight ticket price
     * @param {object} obj.departure - Departure filters
     * @param {number} obj.departure.min - Earliest departure time
     * @param {number} obj.departure.max - Latest departure time
     * @param {object} obj.arrival - Arrival filters
     * @param {number} obj.arrival.min - Earliest arrival time
     * @param {number} obj.arrival.max - Latest arrival time
     * @todo Apply hour to current date set in Toolbar
     * @todo Call fetchFlights action with filters
     *
     * @see FlightToolbarFilters - Event emitter
     */
    async applyFilters({ pricing, departure, arrival }) {
      let format = 'YYYY-MM-DD[T]HH:mm'

      let filters = {
        departureRange: {
          min: date.formatDate(`${this.date}T${departure.min}`, format),
          max: date.formatDate(`${this.date}T${departure.max}`, format)
        },
        arrivalRange: {
          min: date.formatDate(`${this.date}T${arrival.min}`, format),
          max: date.formatDate(`${this.date}T${arrival.max}`, format)
        },
        pricingRange: pricing
      }

      logger.debug('Applying filters')
      logger.debug(filters)
    },
    toggleFilters() {
      this.$refs['filters'].show()
    },
    async updateDestination() {
      // Update route props, and browser history to ensure back button works
      // if fetch fails, a page refresh will also lead to the intended behaviour
      logger.debug('Updating browser history')
      this.$router.push({
        location: this.$router.currentRoute.name,
        query: {
          date: this.departureDate,
          departure: this.departureCity,
          arrival: this.arrivalCity
        }
      })

      logger.debug('Fetching flights using new parameters')
      await this.$store.dispatch('catalog/fetchFlights', {
        date: this.departureDate,
        departure: this.departureCity,
        arrival: this.arrivalCity
      })
    },
    /**
     * Sort flight results by a given preference e.g. price, schedule
     *
     * @param {SortPreference} preference - Array of Flight Class to sort on
     * @example
     * // return flights sorted from least to most expensive
     * sortResults('lowestPrice')
     */
    sortResults(preference) {
      logger.debug(`Sorting flights with ${preference} preference`)
      this.$store.dispatch('catalog/sortFlightsByPreference', preference)
      this.sortSelection = preference
    }
  }
}
</script>

<style lang="sass">
@import '../css/app'

.flight__toolbar
  padding: 0 0.8rem
  @media only screen and (min-device-width: 700px)
      padding: 0 14vw
      margin: 0 20px

.q-field__native
  padding-top: 0 !important

.search__options
  &--input
    color: $primary
    font-weight: bold
    cursor: pointer

  &--editable::before
    content: ""
    position: absolute
    left: 0
    top: 0px
    width: 70%
    border-bottom: $editable-field-border
    margin-top: 2.3em

  &--date
    border-bottom: $editable-field-border

.q-field__label
  top: 24px

.filter__toolbar
  &--header
    background-color: #044389
  &--subheader
    background-color: $grey-2

.filter__option
  &--value
    border-bottom: $editable-field-border
  &--before
    color: rgba(0, 0, 0, 0.87) !important

.blah
  border-bottom: $editable-field-border

.pricing__range
  &--input
    color: $primary

.q-field__marginal
  min-width: 35px !important

.q-select__dialog
  position: absolute
  top: 60px
</style>
