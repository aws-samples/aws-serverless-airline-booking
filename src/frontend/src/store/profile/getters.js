/**
 * Profile [Vuex Module getter](https://vuex.vuejs.org/guide/getters.html) - isAuthenticated
 * @param {object} state - Profile state
 * @returns {boolean} - Whether current user is authenticated
 * @see {@link getSession} for more information on action that calls isAuthenticated
 */
export const isAuthenticated = (state) => {
  return !!state.user
}

/**
 * Profile [Vuex Module getter](https://vuex.vuejs.org/guide/getters.html) - firstName
 * @param {object} state - Profile state
 * @returns {string} - Current user first name attribute in identity provider
 */
export const firstName = (state) => {
  return state.user.attributes?.given_name ?? 'First'
}

/**
 * Profile [Vuex Module getter](https://vuex.vuejs.org/guide/getters.html) - lastName
 * @param {object} state - Profile state
 * @returns {string} - Current user last name attribute in identity provider
 */
export const lastName = (state) => {
  return state.user.attributes?.family_name ?? 'Last Name'
}

/**
 * Profile [Vuex Module getter](https://vuex.vuejs.org/guide/getters.html) - userAttributes
 * @param {object} state - Profile state
 * @returns {object} - All attributes available for current user last name attribute in identity provider e.g. userAttributes.email
 */
export const userAttributes = (state) => {
  return state.user.attributes ?? 'no attributes'
}
