import Booking from '../../shared/models/BookingClass'
// eslint-disable-next-line
import Flight from '../../shared/models/FlightClass'
// @ts-ignore
import { Loading } from 'quasar'
import { processPayment } from './payment';
import axios from 'axios'

// [GraphQL-Example]
// import { listBookingsQuery, processBookingMutation } from './graphql';
// const BookingStatus = Object.freeze({ CONFIRMED: 'CONFIRMED' });
// const bookingFilter = {
//   filter: {
//     status: {
//       eq: BookingStatus.CONFIRMED
//     }
//   }
// };

const bookingEndpoint = process.env.VUE_APP_BookingEndpoint || 'no booking endpoint set'

/**
 *
 * Booking [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - fetchBooking retrieves all bookings for current authenticated customer.
 *
 * It uses SET_BOOKINGS mutation to update Booking state with the latest bookings and flights associated with them.
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @returns {promise} - Promise representing whether bookings from Booking service have been updated in the store
 * @see {@link SET_BOOKINGS} for more info on mutation
 */
export async function fetchBooking ({ commit, rootState, rootGetters }) {
  Loading.show({
    message: 'Loading bookings...'
  })

  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.group('store/bookings/actions/fetchBooking')
  console.log('Credentials retrieved')
  console.log(credentials)

  try {
    // [GraphQL-Example]
    // const result = await axios({
    //   url: bookingEndpoint,
    //   method: 'post',
    //   data: {
    //     query: listBookingsQuery,
    //     variables: {
    //       filter: bookingFilter
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
    //     data: { listBookings: bookingsData }
    //   }
    // } = result

    // [REST-Example]
    // const { data: bookingData } = await axios({
    //   url: bookingEndpoint,
    //   method: 'GET',
    //   headers: {
    //     Authorization: credentials.idToken // API Gateway only accepts ID Token
    //   }
    // })

    // [Mock-Example]
    const { data: bookingData } = await axios.get('/mocks/bookings.json')

    console.info('Booking data response from Bookings....')
    console.log(bookingData)

    const bookings = bookingData.map(booking => new Booking(booking))

    console.info('Committing bookings to the store')
    console.log(bookings)
    commit('SET_BOOKINGS', bookings)
    Loading.hide()

    console.groupEnd()
    return bookings
  } catch (err) {
    Loading.hide()
    const errorMessage = `Error when fetching bookings: ${err.message}`
    console.groupEnd()
    throw new Error(errorMessage)
  }
}

/**
 *
 * Booking [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - createBooking attempts payment charge via Payment service, and it effectively books a flight if payment is accepted.
 *
 * **NOTE**: It doesn't mutate the store
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} obj - Object containing params required to create a booking
 * @param {object} obj.paymentDetails - Payment details captured during flight selection
 * @param {string} obj.paymentDetails.name - Payment card holder's name
 * @param {string} obj.paymentDetails.address_country - Payment card registered country
 * @param {string} obj.paymentDetails.address_postcode - Payment card registered postcode
 * @param {object} obj.paymentDetails.card - Payment card details
 * @param {string} obj.paymentDetails.card.number - Payment card number
 * @param {string} obj.paymentDetails.card.expireMonth - Payment expireMonth e.g 1 (January)
 * @param {string} obj.paymentDetails.card.expireYear - Payment expireYear e.g 2022
 * @param {number} obj.paymentDetails.card.cvc - Payment cvc e.g (444)
 * @param {Flight} obj.outboundFlight - Outbound Flight
 * @param {Flight} [obj.inboundFlight] - Inbound Flight
 * @returns {promise} - Promise representing booking effectively made in the Booking service.
 */
export async function createBooking (
  { rootState, rootGetters },
  { paymentDetails, outboundFlight }
) {
  console.group('store/bookings/actions/createBooking')

  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.log('Credentials retrieved')
  console.log(credentials)

  const chargeToken = await processPayment({
    paymentDetails: paymentDetails,
    outboundFlight: outboundFlight,
    customerEmail: rootGetters['profile/email']
  })

  Loading.show({
    message: 'Payment authorized successfully...'
  })

  console.info('Token received...')
  console.log(chargeToken)

  const bookingProcessId = await processBooking({
    chargeToken,
    outboundFlight,
    credentials
  })

  console.groupEnd()
  return bookingProcessId
}

/**
 *
 * Process Booking function - processBooking uses processBooking mutation to kick off an async Booking Workflow that ultimatelly reserves flight seat, creates a booking reference, collect payment, etc.
 *
 * @param {object} obj - Object containing params to process payment
 * @param {string} obj.chargeToken - Pre-authorized payment token
 * @param {Flight} obj.outboundFlight - Outbound flight
 * @param {object} obj.credentials - JWT tokens
 * @param {object} obj.credentials.idToken - JWT ID token
 * @param {object} obj.credentials.accessToken - JWT Access token
 * @returns {promise} - Promise representing whether Booking Workflow was successfully initiated
 */
async function processBooking ({ chargeToken, outboundFlight, credentials }) {
  console.group('store/bookings/actions/processBooking')
  console.info(`Processing booking for flight ${outboundFlight} with token ${chargeToken}`)
  try {
    Loading.show({
      message: 'Creating a new booking...'
    })

    // [GraphQL-Example]
    // const processBookingInput = {
    //   input: {
    //     paymentToken: chargeToken,
    //     bookingOutboundFlightId: outboundFlight.id
    //   }
    // }

    // const result = await axios({
    //   url: bookingEndpoint,
    //   method: 'post',
    //   data: {
    //     query: processBookingMutation,
    //     variables: {
    //       input: processBookingInput
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
    //     data: { processBookingMutation: { id: bookingProcessId }
    //   }
    // } = result

    // [REST-Example]
    // const data = await axios({
    //   url: bookingEndpoint,
    //   method: 'post',
    //   data: {
    //     paymentToken: chargeToken,
    //     outboundFlight: outboundFlight
    //   },
    //  headers: {
    //     Authorization: credentials.idToken // API Gateway only accepts ID Token
    //   }
    // })

    // [Mock-Example]
    const data = {
      data: {
        processBooking: {
          id: '12345678910'
        }
      }
    }

    console.info('Data received from booking....')
    console.log(data)

    const {
      bookingId: bookingProcessId
    } = data

    console.groupEnd()
    return bookingProcessId
  } catch (err) {
    const errorMessage = `Error when processing booking: ${err.message}`
    console.groupEnd()
    throw errorMessage
  }
}
