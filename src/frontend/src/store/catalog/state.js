import Flight from 'src/shared/models/FlightClass'

/**
 * Catalog [Vuex Module](https://vuex.vuejs.org/guide/modules.html) - It holds flights information from Catalog service.
 *
 * @param {Flight[]} flights - array of flights
 * @param {boolean} loading - toggle for flight loading
 * @param {string} paginationToken - pagination token for flight retrieval
 * @see {@link SET_FLIGHTS} for more info on mutation
 * @see {@link SET_LOADER} for more info on mutation
 * @see {@link fetchFlights} for more info on a module action
 * @see {@link fetchByFlightNumber} for more info on module action
 */
export default {
  flights: [],
  loading: false,
  paginationToken: ''
}
