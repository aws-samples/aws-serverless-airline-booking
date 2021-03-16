<template>
  <q-page class="container">
    <div class="wrapper">
      <div class="heading">
        <div
          class="text-h4 search__headline q-pt-xl"
          data-test="search-headline"
        >
          Where next?
        </div>
      </div>
    </div>
    <div class="search__options">
      <div class="search__options--departure shadow-2 q-mb-xs">
        <q-select
          data-test="search-departure"
          v-model="departureCity"
          stack-label
          label="From"
          placeholder="Where from?"
          class="text-bold"
          input-class="search__options--input"
          :min-characters="3"
          :options="$data.airportSearch_suggestionList"
          :option-label="displayLabel"
          option-value="code"
          map-options
          input-debounce="0"
          @filter="$airportSearch_fuzzySearch"
          display-value-sanitize
          use-input
          hide-dropdown-icon
          clearable
          hide-hint
          hide-selected
          fill-input
          behavior="menu"
          borderless
          item-aligned
        >
          <template v-slot:append>
            <q-btn
              class="search__options--invert"
              icon="swap_vert"
              color="primary"
              round
              @click="swapDirection"
            />
          </template>
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey"> No results </q-item-section>
            </q-item>
          </template>
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
      <div class="search__options--arrival shadow-2 q-mb-lg">
        <q-select
          data-test="search-arrival"
          v-model="arrivalCity"
          stack-label
          label="To"
          placeholder="Where to?"
          class="text-bold"
          input-class="search__options--input"
          :min-characters="3"
          :options="$data.airportSearch_suggestionList"
          :option-label="displayLabel"
          option-value="code"
          map-options
          input-debounce="0"
          @filter="$airportSearch_fuzzySearch"
          display-value-sanitize
          use-input
          hide-dropdown-icon
          clearable
          hide-hint
          hide-selected
          fill-input
          behavior="menu"
          borderless
          item-aligned
        >
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey"> No results </q-item-section>
            </q-item>
          </template>
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

      <div class="search__options--schedule row">
        <div class="col-6 shadow-2 search__options--outbound">
          <q-field
            class="search__date"
            label="Outbound"
            placeholder="When?"
            stack-label
            borderless
            item-aligned
            clearable
          >
            <template v-slot:after>
              <q-icon name="event" color="primary" class="q-pt-lg" />
            </template>
            <template v-slot:control>
              <q-popup-proxy ref="qDateProxy">
                <div>
                  <q-date
                    v-model="departureDate"
                    mask="MMM D, YYYY"
                    color="primary"
                    today-btn
                    @input="() => $refs.qDateProxy.hide()"
                    :options="scheduleOptions"
                  />
                </div>
              </q-popup-proxy>
              {{ departureDate }}
            </template>
          </q-field>
        </div>
        <div class="col"></div>
      </div>
    </div>
    <div class="wrapper row justify-center">
      <div class="col-xs-10 cta">
        <q-btn
          class="cta__button full-width"
          @click="search"
          color="secondary"
          label="Search flights"
          :disable="
            !$v.departureCity.isAirport ||
            !$v.arrivalCity.isAirport ||
            $v.departureCity.$invalid ||
            $v.arrivalCity.$invalid ||
            $v.departureDate.$invalid
          "
        >
          <q-icon
            class="cta__button--direction"
            name="keyboard_arrow_right"
            size="2.6rem"
          />
        </q-btn>
      </div>
    </div>
  </q-page>
</template>

<script>
// @ts-nocheck
import airports from '../store/catalog/airports.json'
import Fuse from 'fuse.js'
import { date } from 'quasar'
import { validationMixin } from 'vuelidate'
import { required, minLength } from 'vuelidate/lib/validators'
import { airportList } from '../shared/mixins/airportSearch'
import { airportSearchMixin } from '../shared/mixins'
import { Logger } from '@aws-amplify/core'

const logger = new Logger('Search')

/**
 * Validate given input against list of valid IATA airports
 * @param {string} value - Given airport input by customer
 * @return {boolean} - Boolean whether given airport is a valid IATA airport from airport list
 */
const isAirport = (value) => {
  value = value ?? ''

  if (value.length < 3) {
    return false
  }

  return airportList.some((airport) => airport.code === value.code)
}

export default {
  /**
   *
   * Search view displays options for searching a flight given a departure, arrival and a date.
   */
  name: 'Search',
  mixins: [validationMixin, airportSearchMixin],
  validations: {
    departureCity: {
      required,
      minLength: minLength(3),
      isAirport
    },
    arrivalCity: {
      required,
      minLength: minLength(3),
      isAirport
    },
    departureDate: {
      required
    }
  },
  data() {
    return {
      /**
       * @param {string} departureCity - Departure city chosen by the customer
       * @param {string} arrivalCity - Arrival city chosen by the customer
       * @param {string} departureDate - Departure date chosen by the customer
       */
      departureCity: '',
      arrivalCity: '',
      departureDate: date.formatDate(Date.now(), 'MMM D, YYYY')
    }
  },
  methods: {
    /**
     * search method collects form data, create queryStrings, and redirects to Search Results view
     */
    search() {
      this.$router.push({
        name: 'searchResults',
        query: {
          date: date.formatDate(this.departureDate, 'YYYY-MM-DD'),
          departure: this.departureCity.code,
          arrival: this.arrivalCity.code
        }
      })
    },
    swapDirection() {
      let departure = this.departureCity
      let arrival = this.arrivalCity
      this.departureCity = arrival
      this.arrivalCity = departure
      logger.debug(
        `Swapped: ${arrival.code} is now departure, and ${departure.code} is arrival`
      )
    },
    scheduleOptions(curDate) {
      let today = date.formatDate(Date.now(), 'YYYY/MM/DD')
      return curDate >= today
    },
    displayLabel(label) {
      // Abort if init or invalid label object
      let isLabel = Object(label) === label && 'city' in label
      if (!isLabel) return null

      return `${label.city} (${label.code})`
    }
  }
}
</script>

<style lang="sass">
@import '../css/app'

.q-field__label
  font-weight: bold
  font-size: 1.25rem !important
  color: $field-label-color
  opacity: .78
  top: 10px

.search__options
  padding: 10vmin 8vmin

  @media (min-device-width: 700px)
    padding: 10vmin 20vmin

  @media (min-device-width: 1024px)
    padding: 10vmin 23vmin

  &--invert
    top: 30px

  &--departure,
  &--arrival,
  &--outbound
    height: 65px !important
    border-radius: 5px
    background-color: white

.search__date
  padding: 8px 14px !important

.q-field__focusable-action
  padding-top: 25px

.cta
  @media (min-width: $breakpoint-sm-min)
    width: 60.333% !important

  @media (min-width: $breakpoint-sm-max)
    width: 57% !important
</style>
