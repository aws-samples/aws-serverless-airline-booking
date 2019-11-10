// @ts-nocheck
/**
 *
 * Booking [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_BOOKINGS mutates Booking state with an array of Bookings as payload.
 * @param {object} state - Vuex Booking Module State
 * @param {Booking[]} bookings - Array of Bookings as payload
 * @see {@link fetchBooking} for more info on action that calls SET_BOOKINGS
 */
export const SET_BOOKINGS = (state, bookings) => {
  if (state.bookings.length === 0) {
    state.bookings = bookings;
  } else {
    // flatten array of bookings and remove possible duplicates due to network issues
    let newBookings = [...bookings, state.bookings].flat(5);
    state.bookings = [...new Set(newBookings)];
  }
};

export const SET_BOOKING_PAGINATION = (state, paginationToken) => {
  state.paginationToken = paginationToken;
};
