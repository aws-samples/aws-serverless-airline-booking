// @ts-nocheck

import Flight from 'src/shared/models/FlightClass'
import { SortPreference } from '../../shared/enums'
import {
  sortByLowestPrice,
  sortByHighestPrice,
  sortByEarliestDeparture,
  sortByLatestDeparture
} from '../../shared/sorters'

/**
 *
 * Catalog [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_FLIGHT mutates Catalog state with an array of Flights as payload.
 * @param {object} state - Vuex Catalog Module State
 * @param {Flight[]} flights - Array of Flights
 * @see {@link fetchFlights} for more info on action that calls SET_FLIGHTS
 * @see {@link fetchByFlightNumber} for more info on action that calls SET_FLIGHTS
 */
export const SET_FLIGHTS = async (state, flights) => {
  if (state.flights.length === 0) {
    state.flights = flights
  } else {
    // flatten array of flights and remove possible duplicates due to network issues
    let newFlights = [...flights, state.flights].flat(5)
    state.flights = [...new Set(newFlights)]
  }
}

/**
 *
 * Catalog [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_LOADER mutates Catalog state to control content loader when necessary.
 * @param {object} state - Vuex Catalog Module State
 * @param {boolean} isLoading - Boolean that controls whether content loader should be running
 * @see {@link fetchFlights} for more info on action that calls SET_LOADER
 * @see {@link fetchByFlightNumber} for more info on action that calls SET_LOADER
 */
export const SET_LOADER = (state, isLoading) => {
  state.loading = isLoading
}

export const SET_FLIGHT_PAGINATION = (state, paginationToken) => {
  state.paginationToken = paginationToken
}

/**
 * Catalog [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SORT_FLIGHTS mutates Catalog flights state to sort flights with a given preference.
 * @param {object} state - Vuex Catalog Module State
 * @param {Flight[]} state.flights - Array of Flights
 * @param {SortPreference} preference - Sorting preference
 */
export const SORT_FLIGHTS = (state, preference) => {
  switch (preference) {
    case SortPreference.LowestPrice:
      state.flights = sortByLowestPrice(state.flights)
      break

    case SortPreference.HighestPrice:
      state.flights = sortByHighestPrice(state.flights)
      break

    case SortPreference.EarliestDeparture:
      state.flights = sortByEarliestDeparture(state.flights)
      break

    case SortPreference.LatestDeparture:
      state.flights = sortByLatestDeparture(state.flights)
      break

    default:
      console.warn(`Unknown sorting preference: ${preference}, skipping...`)
      break
  }
}
