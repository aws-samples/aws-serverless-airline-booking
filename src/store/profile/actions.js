import { Auth } from 'aws-amplify'

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
 */
export function getSession ({ commit, getters }) {
  return new Promise((resolve, reject) => {
    Auth.currentAuthenticatedUser()
      .then(user => {
        if (!getters.isAuthenticated) {
          commit('SET_USER', user)
        }
        resolve()
      })
      .catch(err => {
        console.log(err)
        if (getters.isAuthenticated) {
          commit('SET_USER')
        }
        reject(err)
      })
  })
}
