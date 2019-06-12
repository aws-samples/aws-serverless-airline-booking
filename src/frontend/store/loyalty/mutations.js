/**
 *
 * Profile [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_LOYALTY mutates Loyalty state with given loyalty info as payload.
 * @param {object} state - Vuex Profile Module State
 * @param {object} loyalty - Payload to bet set as loyalty info
 * @param {string} loyalty.level - Current loyalty level
 * @param {number} loyalty.points - Current amount of loyalty points
 * @param {number} loyalty.remainingPoints - Loyalty points necessary to reach next loyalty tier
 * @param {number} loyalty.membershipNumber - Loyalty membership number
 * @param {object} loyalty.customer - Loyalty customer ID
 * @see {@link fetchLoyalty} for more info on action that calls SET_LOYALTY
 */
export const SET_LOYALTY = async (state, loyalty) => {
  state.loyalty = loyalty;
};
