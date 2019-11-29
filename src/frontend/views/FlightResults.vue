<template>
  <q-page class="container">
    <flight-toolbar
      v-if="date && departure && arrival"
      :departure="departure"
      :arrival="arrival"
    />
    <q-page-sticky
      v-if="date && departure && arrival"
      position="top-right"
      :offset="[15, 13]"
    >
      <q-fab flat icon="tune" direction="left">
        <q-fab-action color="secondary" icon="attach_money" glossy>
          <q-popup-edit
            @save="setPrice"
            title="Max Price filter"
            buttons
            v-model="maxPriceFilter"
          >
            <q-slider
              color="secondary"
              :min="minimumPrice"
              :max="maximumPrice"
              label
              label-always
              v-model="maxPriceFilter"
              class="filter__price"
            />
          </q-popup-edit>
        </q-fab-action>
        <q-fab-action color="secondary" icon="schedule" glossy>
          <q-popup-edit title="Schedule filter">
            <q-datetime
              type="time"
              format24h
              format="HH:mm"
              format-model="date"
              placeholder="Depart at"
              clearable
              @input="setDeparture"
              v-model="departureTimeFilter"
              class="filter__departure"
            />
            <q-datetime
              type="time"
              format24h
              format="HH:mm"
              format-model="date"
              placeholder="Arrive by"
              clearable
              @input="setArrival"
              v-model="arrivalTimeFilter"
              class="filter__arrival"
            />
          </q-popup-edit>
        </q-fab-action>
        <q-fab-action
          color="secondary"
          icon="cancel"
          @click="filteredFlights = flights"
          glossy
          class="filter__cta"
        />
      </q-fab>
    </q-page-sticky>
    <div class="heading">
      <div class="q-headline text-primary text-center">
        <div class="loader" v-if="loading">
          <flight-loader></flight-loader>
        </div>
        <div v-if="filteredFlights.length && !loading">
          <span class="results__headline" data-test="results-headline"
            >Select your flight</span
          >
        </div>
        <div
          v-if="!filteredFlights.length && !loading"
          class="heading__error row"
        >
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
    <div class="results__flights" v-if="filteredFlights.length && !loading">
      <router-link
        :to="{
          name: 'selectedFlight',
          params: { flight: flight },
          query: { flightId: flight.id }
        }"
        v-for="flight in filteredFlights"
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
  </q-page>
</template>

<script>
// @ts-nocheck
import FlightCard from "../components/FlightCard";
import FlightToolbar from "../components/FlightToolbar";
import FlightLoader from "../components/FlightLoader";
import { mapState, mapGetters } from "vuex";
import { priceFilter, scheduleFilter } from "../shared/mixins/filters";
import { priceSorter, scheduleSorter } from "../shared/mixins/sorters";

/**
 * Flight Results view displays a collection of Flights from Catalog.
 */
export default {
  name: "FlightResults",
  components: {
    FlightCard,
    FlightToolbar,
    FlightLoader
  },
  mixins: [priceFilter, scheduleFilter, priceSorter, scheduleSorter],
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
  /**
   * @param {Flight[]} filteredFlights - List of Flights filtered by departure, price or schedule
   * @param {string} departureTimeFilter - Departure schedule one wishes to filter flights by
   * @param {string} arrivalTimeFilter - Arrival schedule one wishes to filter flights by
   * @param {string} maxPriceFilter - Maximum price one wishes to limit flights to
   */
  data() {
    return {
      filteredFlights: [],
      departureTimeFilter: "",
      arrivalTimeFilter: "",
      maxPriceFilter: 300
    };
  },
  mounted() {
    /** authentication guards prevent authenticated users to view Flights
     * however, the component doesn't stop from rendering asynchronously
     * this guarantees we attempt talking to Catalog service
     * if our authentication guards && profile module have an user in place
     */
    if (this.isAuthenticated) {
      this.loadFlights();
    }
  },
  methods: {
    /**
     * loadFlights method fetches all flights via catalog API
     */
    async loadFlights() {
      try {
        if (this.isAuthenticated) {
          await this.$store.dispatch("catalog/fetchFlights", {
            date: this.date,
            departure: this.departure,
            arrival: this.arrival,
            paginationToken: this.paginationToken
          });

          this.filteredFlights = this.sortByDeparture(this.flights);
        }
      } catch (error) {
        console.error(error);
        this.$q.notify(
          `Error while fetching Flight results - Check browser console messages`
        );
      }
    },
    /**
     * setPrice method updates maxPriceFilter and filter flights via filterByMaxPrice mixin
     */
    setPrice() {
      let flights = this.filterByMaxPrice(this.flights, this.maxPriceFilter);
      flights = this.sortByPrice(flights);
      this.filteredFlights = flights;
    },
    /**
     * setDeparture method updates departureTimeFilter and filter flights via filterBySchedule mixin
     */
    setDeparture() {
      let flights = this.filterBySchedule(this.flights, {
        departure: this.departureTimeFilter
      });
      flights = this.sortByDeparture(flights);
      this.filteredFlights = flights;
    },
    /**
     * setArrival method updates arrivalTimeFilter and filter flights via filterBySchedule mixin
     */
    setArrival() {
      this.filteredFlights = this.filterBySchedule(this.flights, {
        arrival: this.arrivalTimeFilter
      });
    }
  },
  /**
   * @param {Flight} flights - Flights state from Flights module
   * @param {boolean} loading - Loader state used to control Flight Loader when fetching flights
   * @param {boolean} isAuthenticated - Getter from Profile module
   * @param {number} maximumPrice - Maximum ticket price calculated across all available flights
   * @param {number} minimumPrice - Minimum ticket price calculated across all available flights
   */
  computed: {
    ...mapState({
      flights: state => state.catalog.flights,
      loading: state => state.catalog.loading,
      paginationToken: state => state.catalog.paginationToken
    }),
    ...mapGetters("profile", ["isAuthenticated"]),
    maximumPrice: function() {
      return Math.max(...this.flights.map(filter => filter.ticketPrice), 500);
    },
    minimumPrice: function() {
      return Math.min(...this.flights.map(filter => filter.ticketPrice), 1);
    }
  }
};
</script>

<style lang="stylus" scoped>
@import '~variables'

.heading
  margin-top 5.5rem

.heading__error--cta
  margin auto
  margin-top 10vh
  width 70vw

.loader
  width 150%
</style>
