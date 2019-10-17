import Loyalty from '../../shared/models/LoyaltyClass'
// @ts-ignore
import { Loading } from 'quasar'

import axios from 'axios'

// const loyaltyEndpoint = 'https://489ibclmwd.execute-api.eu-west-1.amazonaws.com/Prod'

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
 * // exerpt from src/views/Profile.vue
 * async mounted() {
 *    if (this.isAuthenticated) {
 *        await this.$store.dispatch("loyalty/fetchLoyalty");
 *    }
 * }
 */
export async function fetchLoyalty ({ commit, rootState, rootGetters }) {
  Loading.show({
    message: 'Loading profile...'
  })

  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.log('Credentials retrieved')
  console.log(credentials)

  try {
    // [GraphQL-Example]
    // const fetchLoyaltyQuery = `query getLoyalty_status($cust_id: ID!) {
    //   getLoyalty_status(cust_id: $cust_id) {
    //     cust_id
    //     points
    //     tier
    //     remaining_pointss
    //   }
    // }`

    // const result = await axios({
    //   url: loyaltyEndpoint,
    //   method: 'post',
    //   data: {
    //     query: fetchLoyaltyQuery,
    //     variables: {
    //       cust_id: user.id
    //     }
    //   },
    //   headers: {
    //     Authorization: credentials.accessToken,
    //     'Content-Type': 'application/json'
    //   }
    // })

    // const {
    //   data: {
    //     data: { getLoyalty_status: loyaltyData }
    //   }
    // } = result

    // [REST-Example]
    // const { data: loyaltyData } = await axios.get(loyaltyEndpoint + '/getLoyaltyPoints', {
    //   headers: {
    //     Authorization: credentials.idToken
    //   }
    // })

    // [Mock-Example]
    const { data: loyaltyData } = await axios.get('/mocks/loyalty.json')

    const loyalty = new Loyalty(loyaltyData)

    console.info('Committing loyalty to the store')
    console.log(loyalty)
    commit('SET_LOYALTY', loyalty)

    Loading.hide()
    return loyalty
  } catch (err) {
    Loading.hide()
    throw new Error(err)
  }
}
