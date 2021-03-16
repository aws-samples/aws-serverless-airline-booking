import Auth from '@aws-amplify/auth'

/**
 *
 * Profile [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - getSession [retrieves current authenticated user info](https://aws-amplify.github.io/docs/js/authentication) from [Amazon Cognito](https://aws.amazon.com/cognito/).
 *
 * It uses SET_USER mutation to update Profile state with latest information about authenticated user.
 *
 * When user is not authenticated, it resets Profile state by calling SET_USER mutation without user data
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} context.commit - Vuex mutation function (context.commit)
 * @param {object} context.getters - Vuex mutation function (context.commit)
 * @see {@link isAuthenticated} for more info on getter
 * @see {@link SET_USER} for more info on mutation
 * @returns {promise} - Promise representing updated profile information in the store
 * @example
 * // exerpt from src/pages/Profile.vue
 * onAuthUIStateChange((authState, authData) => {
 *   if (authState === AuthState.SignedOut) {
 *     this.$store
 *       .dispatch('profile/getSession')
 *       .catch(
 *         this.$router.push({ name: 'auth', query: { redirectTo: 'home' } })
 *       )
 *   }
 * })
 *
 * // exerpt from src/router/index.js as a Route Guard
 * Router.beforeEach(async (to, from, next) => {
 *   const isProtected = to.matched.some((record) => record.meta.requiresAuth)
 *   if (isProtected) {
 *     console.info(`Page ${to.fullPath} requires Auth!`)
 *     if (!store.getters['profile/isAuthenticated']) {
 *       try {
 *         await store.dispatch('profile/getSession')
 *         next()
 *       } catch (err) {
 *         next({ name: 'auth', query: { redirectTo: to.name } })
 *       }
 *     }
 *   }
 *   next()
 * })
 */
export async function getSession({ commit, getters }) {
  console.group('store/profile/actions/getSession')
  console.log('Fetching current session')
  try {
    const user = await Auth.currentAuthenticatedUser()
    if (!getters.isAuthenticated) {
      commit('SET_USER', user)
    }
  } catch (err) {
    console.log(err)
    if (getters.isAuthenticated) {
      commit('SET_USER')
    }
    throw new Error(err)
  }
  console.groupEnd()
}
