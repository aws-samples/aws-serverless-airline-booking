import Flight from '../../shared/models/FlightClass'

// [Mock-Example]
import axios from 'axios'

// const catalogEndpoint = 'https://a5otqx8fob.execute-api.eu-west-1.amazonaws.com/Prod'

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
export async function fetchFlights ({ commit, rootGetters }, { date, departure, arrival }) {
  commit('SET_LOADER', true)

  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.log('Credentials retrieved')
  console.log(credentials)

  try {
    // [GraphQL-Example]
    // listFlights query filter
    // const flightFilter = {
    //   filter: {
    //     departureDate: {
    //       beginsWith: date
    //     },
    //     departureAirportCode: {
    //       eq: departure
    //     },
    //     arrivalAirportCode: {
    //       eq: arrival
    //     },
    //     seatAllocation: {
    //       gt: 0
    //     }
    //   }
    // };

    // const listFlightQuery = `query listFlights($filter: ModelFlightFilterInput) {
    //   listFlights(filter: $filter) {
    //         items {
    //           id
    //           departureDate
    //           departureAirportCode
    //           departureAirportName
    //           departureCity
    //           departureLocale
    //           arrivalDate
    //           arrivalAirportCode
    //           arrivalAirportName
    //           arrivalCity
    //           arrivalLocale
    //           ticketPrice
    //           ticketCurrency
    //           flightNumber
    //           seatAllocation
    //         }
    //   }
    // }`

    // const result = await axios({
    //   url: catalogEndpoint,
    //   method: 'post',
    //   data: {
    //     query: listFlightsQuery,
    //     variables: {
    //       filter: flightFilter
    //     }
    //   },
    //   headers: {
    //     Authorization: credentials.accessToken,
    //     'Content-Type': 'application/json'
    //   }
    // })

    // const {
    //   data: {
    //     data: { listFlights: flightData }
    //   }
    // } = result

    // [REST-Example]
    // const { data: flightData } = await axios.get(catalogEndpoint + '/getFlights', {
    //   params: {
    //     arrival: arrival,
    //     departure: departure,
    //     date: date
    //   },
    //  headers: {
    //     Authorization: credentials.idToken // API Gateway only accepts ID Token
    //   }
    // })

    // [Mock-Example]
    const { data: flightData } = await axios.get('/mocks/flights.json')

    // data mutations happen within a Flight class
    // here we convert graphQL results into an array of Flights
    // before comitting to Vuex State Management
    // const flights = flightData.Items.map(flight => new Flight(flight))
    const flights = flightData.map(flight => new Flight(flight))

    console.info('Committing Flights to the store...')
    console.log(flights)

    commit('SET_FLIGHTS', flights)
    commit('SET_LOADER', false)
  } catch (error) {
    console.error(error)
    commit('SET_LOADER', false)
    throw error
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
export async function fetchByFlightId ({ commit, rootGetters }, { flightId }) {
  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.log('Credentials retrieved')
  console.log(credentials)

  try {
    commit('SET_LOADER', true)

    // [GraphQL-Example]
    // const getFlightQuery = `query GetFlight($id: ID!) {
    //     getFlight(id: $id) {
    //       id
    //       departureDate
    //       departureAirportCode
    //       departureAirportName
    //       departureCity
    //       departureLocale
    //       arrivalDate
    //       arrivalAirportCode
    //       arrivalAirportName
    //       arrivalCity
    //       arrivalLocale
    //       ticketPrice
    //       ticketCurrency
    //       flightNumber
    //       seatAllocation
    //     }
    // }`

    // const result = await axios({
    //   url: catalogEndpoint,
    //   method: 'post',
    //   data: {
    //     query: getFlightQuery,
    //     variables: {
    //       id: flightId
    //     }
    //   },
    //   headers: {
    //     Authorization: credentials.accessToken,
    //     'Content-Type': 'application/json'
    //   }
    // })

    // const {
    //   data: {
    //     data: { listFlights: flightData }
    //   }
    // } = result

    // [REST Example]
    // var { data: flightData } = await axios.get(catalogEndpoint + '/getFlights', {
    //   params: {
    //     id: flightId
    //   },
    //  headers: {
    //     Authorization: credentials.idToken // API Gateway only accepts ID Token
    //   }
    // })

    // [Mock-Example]
    var { data: flightData } = await axios.get('/mocks/flights.json')

    flightData = flightData.find(flight => flight.id === flightId)

    console.info('Flight received from Catalog...')
    console.log(flightData)

    const flight = new Flight(flightData)
    commit('SET_LOADER', false)
    return flight
  } catch (error) {
    console.error(error)
    commit('SET_LOADER', false)
    throw error
  }
}
