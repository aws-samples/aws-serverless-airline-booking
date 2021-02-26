import Loyalty from '../../shared/models/LoyaltyClass'
// @ts-ignore
import { Loading } from 'quasar'

import { API, graphqlOperation } from '@aws-amplify/api'
import { getLoyalty } from './graphql'

/**
 * Loyalty [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - fetchLoyalty retrieves current authenticated user loyalty info from Loyalty service.
 *
 * It uses SET_LOYALTY mutation to update Loyalty state with the latest information.
 *
 * It also uses Quasar Loading spinner when fetching data from Loyalty service.
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} context.commit - Vuex mutation function (context.commit)
 * @returns {promise} - Promise representing updated whether loyalty information has been updated in the store
 * @see {@link SET_LOYALTY} for more info on mutation
 * @example
 * // excerpt from src/pages/Profile.vuw
 * async mounted() {
 *    if (this.isAuthenticated) {
 *        await this.$store.dispatch("loyalty/fetchLoyalty");
 *    }
 * }
 */
export async function fetchLoyalty({ commit }) {
  Loading.show({
    message: 'Loading profile...'
  })

  console.group('store/loyalty/actions/fetchLoyalty')
  try {
    console.log('Fetching loyalty data')
    const {
      // @ts-ignore
      data: { getLoyalty: loyaltyData }
    } = await API.graphql(graphqlOperation(getLoyalty))
    const loyalty = new Loyalty(loyaltyData)

    console.log(loyalty)
    commit('SET_LOYALTY', loyalty)

    Loading.hide()
    console.groupEnd()
  } catch (err) {
    Loading.hide()
    throw new Error(err)
  }
}
