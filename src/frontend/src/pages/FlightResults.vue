<template>
  <q-page class="container">
    <flight-toolbar v-if="date && departure && arrival" />
    <div class="heading">
      <div class="text-primary text-center">
        <div class="loader" v-if="loading">
          <flight-loader></flight-loader>
        </div>
        <div v-if="flights.length && !loading">
          <span class="results__headline text-h5" data-test="results-headline"
            >Select your flight</span
          >
        </div>
        <div v-if="!flights.length && !loading" class="heading__error row">
          <span
            class="justify-center full-width results__error"
            data-test="results-error"
            >No results found</span
          >
          <transition enter-active-class="animated bounce" appear>
            <q-btn
              class="cta__button heading__error--cta"
              color="secondary"
              label="Search flights"
              icon="keyboard_arrow_left"
              :to="{ name: 'home' }"
            >
            </q-btn>
          </transition>
        </div>
      </div>
    </div>
    <div class="results__flights" v-if="flights.length && !loading">
      <router-link
        :to="{
          name: 'selectedFlight',
          params: { flight: flight },
          query: { flightId: flight.id }
        }"
        v-for="flight in flights"
        :key="flight.id"
      >
        <flight-card :details="flight" />
      </router-link>
    </div>
    <div class="wrapper">
      <q-btn
        v-if="paginationToken"
        @click="loadFlights"
        class="cta__button"
        color="secondary"
        size="1rem"
        label="Load more flights?"
        data-test="flight-pagination"
      />
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
import FlightCard from '../components/FlightCard'
import FlightToolbar from '../components/FlightToolbar'
import FlightLoader from '../components/FlightLoader'
import { mapState, mapGetters } from 'vuex'

/**
 * Flight Results view displays a collection of Flights from Catalog.
 */
export default {
  name: 'FlightResults',
  components: {
    FlightCard,
    FlightToolbar,
    FlightLoader
  },
  /**
   * @param {string} date - Departure date one wishes to travel by
   * @param {string} departure - Departure airport IATA one wishes to travel from
   * @param {string} arrival - Arrival airport IATA one wishes to travel to
   */
  props: {
    date: { type: String, required: true },
    departure: { type: String, required: true },
    arrival: { type: String, required: true }
  },
  mounted() {
    /** authentication guards prevent authenticated users to view Flights
     * however, the component doesn't stop from rendering asynchronously
     * this guarantees we attempt talking to Catalog service
     * if our authentication guards && profile module have an user in place
     */
    if (this.isAuthenticated) {
      this.loadFlights()
    }
  },
  /**
   * @param {Flight} flights - Flights state from Flights module
   * @param {boolean} loading - Loader state used to control Flight Loader when fetching flights
   * @param {boolean} isAuthenticated - Getter from Profile module
   * @param {boolean} paginationToken - Flights pagination token
   */
  computed: {
    ...mapState({
      flights: (state) => state.catalog.flights,
      loading: (state) => state.catalog.loading,
      paginationToken: (state) => state.catalog.paginationToken
    }),
    ...mapGetters('profile', ['isAuthenticated'])
  },
  methods: {
    /**
     * loadFlights method fetches all flights via catalog API
     */
    async loadFlights() {
      try {
        if (this.isAuthenticated) {
          await this.$store.dispatch('catalog/fetchFlights', {
            date: this.date,
            departure: this.departure,
            arrival: this.arrival,
            paginationToken: this.paginationToken
          })
        }
      } catch (error) {
        console.error(error)
        this.$q.notify(
          `Error while fetching Flight results - Check browser console messages`
        )
      }
    }
  }
}
</script>

<style lang="sass" scoped>
@import '../css/app'

.heading__error--cta
  margin: auto
  margin-top: 10vh
  width: 70vw

.loader
  width: 150%
</style>
