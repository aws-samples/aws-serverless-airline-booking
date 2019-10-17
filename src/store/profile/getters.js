/**
 * Profile [Vuex Module getter](https://vuex.vuejs.org/guide/getters.html) - isAuthenticated
 * @param {object} state - Profile state
 * @returns {boolean} - Whether current user is authenticated
 * @see {@link getSession} for more information on action that calls isAuthenticated
 */
export const isAuthenticated = state => {
  // Uncomment line below once Auth has been setup
  return !!state.user
  // [Mock-Example]
  // Disables route guard when auth isn't setup
  // return true
}

export const idToken = state => {
  const session = (state.user && state.user.signInUserSession) || 'no user session'
  const idToken = (session && session.idToken && session.idToken.jwtToken) || 'not auth'

  return idToken
}

export const accessToken = state => {
  const session = (state.user && state.user.signInUserSession) || 'no user session'
  const accessToken = (session && session.accessToken && session.accessToken.jwtToken) || 'not auth'

  return accessToken
}
