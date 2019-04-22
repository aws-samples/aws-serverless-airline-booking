// @ts-nocheck
/**
 *
 * Booking [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_BOOKINGS mutates Booking state with an array of Bookings as payload.
 * @param {object} state - Vuex Booking Module State
 * @param {Booking[]} bookings - Array of Bookings as payload
 * @see {@link fetchBooking} for more info on action that calls SET_BOOKINGS
 */
export const SET_BOOKINGS = (state, bookings) => {
  state.bookings = bookings;
};
