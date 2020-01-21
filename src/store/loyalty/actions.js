import Loyalty from '../../shared/models/LoyaltyClass'
// @ts-ignore
import { Loading } from 'quasar'

import axios from 'axios'

const loyaltyEndpoint = process.env.VUE_APP_LoyaltyEndpoint || 'no loyalty endpoint set'

// [GraphQL-Example]
// import { fetchLoyaltyQuery } from './graphql'

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
 */
export async function fetchLoyalty ({ commit, rootState, rootGetters }) {
  Loading.show({
    message: 'Loading profile...'
  })

  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.group('store/loyalty/actions/fetchLoyalty')
  console.log('Credentials retrieved')
  console.log(credentials)

  try {
    // [GraphQL-Example]
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

    // Deconstructing JSON response: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment#Object_destructuring
    // const {
    //   data: {
    //     data: { getLoyalty_status: loyaltyData }
    //   }
    // } = result

    // [REST-Example]
    // const { data: loyaltyData } = await axios.get(loyaltyEndpoint, {
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
    console.groupEnd()
    return loyalty
  } catch (err) {
    Loading.hide()
    console.log(err)
    console.groupEnd()
    throw err
  }
}
