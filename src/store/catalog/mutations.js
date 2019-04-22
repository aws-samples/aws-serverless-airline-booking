// @ts-nocheck
/**
 *
 * Catalog [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_FLIGHT mutates Catalog state with an array of Flights as payload.
 * @param {object} state - Vuex Catalog Module State
 * @param {Flight[]} flights - Array of Flights as payload
 * @see {@link fetchFlights} for more info on action that calls SET_FLIGHTS
 * @see {@link fetchByFlightNumber} for more info on action that calls SET_FLIGHTS
 */
export const SET_FLIGHTS = async (state, flights) => {
  state.flights = flights;
};

/**
 *
 * Catalog [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_LOADER mutates Catalog state to control content loader when necessary.
 * @param {object} state - Vuex Catalog Module State
 * @param {boolean} isLoading - Boolean that controls whether content loader should be running
 * @see {@link fetchFlights} for more info on action that calls SET_LOADER
 * @see {@link fetchByFlightNumber} for more info on action that calls SET_LOADER
 */
export const SET_LOADER = (state, isLoading) => {
  state.loading = isLoading;
};
