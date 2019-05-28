import Flight from "../../shared/models/FlightClass";
import { API, graphqlOperation } from "aws-amplify";
import { listFlights, getFlight } from "../../graphql/queries";

/**
 *
 * Catalog [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - fetchFlights retrieves all flights for a given date, departure and arrival from Catalog service.
 *
 * It uses SET_FLIGHTS mutation to update Catalog state with the latest flights.
 *
 * It also controls Flight Loader when fetching data from Catalog service.
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} obj - Object containing params to filter flights from catalog
 * @param {Date} obj.date - Date in DD-MM-YYYY format
 * @param {string} obj.departure - Airport IATA to be filtered as departure
 * @param {string} obj.arrival - Airport IATA to be filtered as arrival
 * @returns {promise} - Promise representing whether flights from Catalog have been updated in the store
 * @see {@link SET_FLIGHTS} for more info on mutation
 * @see {@link SET_LOADER} for more info on mutation
 * @example
 * // exerpt from src/views/FlightResults.vue
 * async mounted() {
 * // @ts-ignore
 * if (this.isAuthenticated) {
 *    await this.$store.dispatch("catalog/fetchFlights", {
 *       date: this.date,
 *       departure: this.departure,
 *       arrival: this.arrival
 *    });
 *
 *    this.filteredFlights = this.sortByDeparture(this.flights);
 * }
 */
export async function fetchFlights({ commit }, { date, departure, arrival }) {
  commit("SET_LOADER", true);
  try {
    // listFlights query filter
    const flightFilter = {
      filter: {
        departureDate: {
          beginsWith: date
        },
        departureAirportCode: {
          eq: departure
        },
        arrivalAirportCode: {
          eq: arrival
        }
      }
    };

    const {
      // @ts-ignore
      data: {
        listFlights: { items: flightData }
      }
    } = await API.graphql(graphqlOperation(listFlights, flightFilter));

    // data mutations happen within a Flight class
    // here we convert graphQL results into an array of Flights
    // before comitting to Vuex State Management
    const flights = flightData.map(flight => new Flight(flight));

    commit("SET_FLIGHTS", flights);
    commit("SET_LOADER", false);
  } catch (error) {
    console.error(error);
    commit("SET_LOADER", false);
    throw error;
  }
}

/**
 *
 * Catalog [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - fetchByFlightId retrieves a unique flight from Catalog service. Flight Number may be reused but not ID.
 *
 * Similarly to fetchFlights, it also controls Flight Loader when fetching data from Catalog service.
 *
 * **NOTE**: It doesn't mutate the store
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} obj - Object containing params to filter flights from catalog
 * @param {string} obj.flightId - Flight Unique Identifier
 * @returns {promise} - Promise representing flight from Catalog service.
 * @see {@link SET_LOADER} for more info on mutation
 * @example
 * // exerpt from src/views/FlightSelection.vue
 * async beforeMount() {
 *    if (this.isAuthenticated) {
 *        if (!this.flight) {
 *            this.selectedFlight = await this.$store.dispatch("catalog/fetchByFlightId", {
 *              flightId: this.flightId
 *            });
 *        }
 *    }
 * },
 */
export async function fetchByFlightId({ commit }, { flightId }) {
  try {
    commit("SET_LOADER", true);
    const {
      // @ts-ignore
      data: { getFlight: flightData }
    } = await API.graphql(graphqlOperation(getFlight, { id: flightId }));

    const flight = new Flight(flightData);
    commit("SET_LOADER", false);
    return flight;
  } catch (error) {
    console.error(error);
    commit("SET_LOADER", false);
    throw error;
  }
}
