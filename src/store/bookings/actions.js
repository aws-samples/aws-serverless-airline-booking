import Booking from '../../shared/models/BookingClass'
// eslint-disable-next-line
import Flight from '../../shared/models/FlightClass'
// @ts-ignore
import { Loading } from 'quasar'
import axios from 'axios'

// [GraphQL-Example]
// import { API, graphqlOperation } from "aws-amplify";
// import {
//   processBooking as processBookingMutation,
//   listBookings
// } from "./graphql";

const paymentEndpoint = 'https://PAYMENT_ENDPOINT'
// const bookingEndpoint = "https://CATALOG_ENDPOINT"

/**
 *
 * Booking [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - fetchBooking retrieves all bookings for current authenticated customer.
 *
 * It uses SET_BOOKINGS mutation to update Booking state with the latest bookings and flights associated with them.
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @returns {promise} - Promise representing whether bookings from Booking service have been updated in the store
 * @see {@link SET_BOOKINGS} for more info on mutation
 * @example
 * // exerpt from src/views/Bookings.vue
 * import { mapState, mapGetters } from "vuex";
 * ...
 * async mounted() {
 *    if (this.isAuthenticated) {
 *       await this.$store.dispatch("bookings/fetchBooking");
 *    }
 * },
 * computed: {
 *    ...mapState({
 *        bookings: state => state.bookings.bookings
 *    }),
 *    ...mapGetters("profile", ["isAuthenticated"])
 * }
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
    // const BookingStatus = Object.freeze({ CONFIRMED: 'CONFIRMED' });
    // const bookingFilter = {
    //   filter: {
    //     status: {
    //       eq: BookingStatus.CONFIRMED
    //     }
    //   }
    // };

    // const listBookingsQuery = `query ListBookings(
    //   $filter: ModelBookingFilterInput
    //   $limit: Int
    //   $nextToken: String
    // ) {
    //   listBookings(filter: $filter, limit: $limit, nextToken: $nextToken) {
    //     items {
    //       id
    //       status
    //       outboundFlight {
    //         id
    //         departureDate
    //         departureAirportCode
    //         departureAirportName
    //         departureCity
    //         departureLocale
    //         arrivalDate
    //         arrivalAirportCode
    //         arrivalAirportName
    //         arrivalCity
    //         arrivalLocale
    //         ticketPrice
    //         ticketCurrency
    //         flightNumber
    //         seatAllocation
    //       }
    //       createdAt
    //       bookingReference
    //     }
    //     nextToken
    //   }
    // }`

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

    // const {
    //   data: {
    //     data: { listBookings: bookingsData }
    //   }
    // } = result

    // [REST-Example]
    // const { data: bookingData } = await axios({
    //   url: bookingEndpoint + '/bookings',
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
    console.error(err)
    console.groupEnd()
    throw new Error(err)
  }
}

/**
 *
 * Booking [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - createBooking attempts payment charge via Payment service, and it effectively books a flight if payment is accepted.
 *
 * **NOTE**: It doesn't mutate the store
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} obj - Object containing params required to create a booking
 * @param {object} obj.paymentToken - Stripe JS Payment token object
 * @param {Flight} obj.outboundFlight - Outbound Flight
 * @param {Flight} [obj.inboundFlight] - Inbound Flight
 * @returns {promise} - Promise representing booking effectively made in the Booking service.
 * @example
 * // exerpt from src/views/FlightSelection.vue
 * methods: {
 *    async payment() {
 *        let options = {
 *           name: this.form.name,
 *           address_zip: this.form.postcode,
 *           address_country: this.form.country
 *        }
 *
 *        try {
 *            const { token, error } = await stripe.createToken(card, options);
 *            this.token.details = token;
 *            this.token.error = error;
 *
 *            if (this.token.error) throw this.token.error;
 *
 *            await this.$store.dispatch("bookings/createBooking", {
 *              paymentToken: this.token,
 *              outboundFlight: this.selectedFlight
 *            });
 *        ...
 *        }
 */
export async function createBooking (
  { rootState, rootGetters },
  { paymentToken, outboundFlight }
) {
  // const user = {
  //   credentials: rootState.profile.user.signInUserSession.idToken.jwtToken,
  //   id: rootState.profile.user.attributes.sub,
  //   email: rootState.profile.user.attributes.email || 'customerEmail@address.com'
  // }

  const credentials = {
    idToken: rootGetters['profile/idToken'],
    accessToken: rootGetters['profile/accessToken']
  }

  console.group('store/bookings/actions/createBooking')
  console.log('Credentials retrieved')
  console.log(credentials)

  const chargeToken = await processPayment({
    endpoint: paymentEndpoint,
    paymentToken: paymentToken,
    outboundFlight: outboundFlight,
    // customerEmail: rootState.profile.user.attributes.email
    customerEmail: 'email@address.com'
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
 * Process Payment function - processPayment calls Payment endpoint to pre-authorize charge upon tokenized payment details
 *
 * @param {object} obj - Object containing params to process payment
 * @param {string} obj.endpoint - Payment endpoint
 * @param {object} obj.paymentToken - Tokenized payment info
 * @param {object} obj.paymentToken.details - Tokenized payment details including last4, id, etc.
 * @param {object} obj.paymentToken.id - Payment token
 * @param {Flight} obj.outboundFlight - Outbound flight
 * @param {string} obj.customerEmail - Customer Email address for payment notification
 * @returns {promise} - Promise representing whether payment was successfully pre-authorized
 * @example
 *   let chargeToken = await processPayment({
 *      endpoint: paymentEndpoint,
 *      paymentToken,
 *      outboundFlight,
 *      customerEmail
 *   });
 */
async function processPayment ({
  endpoint,
  paymentToken,
  outboundFlight,
  customerEmail
}) {
  Loading.show({
    message: 'Charging a pre-authorization...'
  })

  if (!paymentToken) throw new Error('Invalid payment token')

  const chargeData = {
    amount: outboundFlight.ticketPrice || '0',
    currency: outboundFlight.ticketCurrency || 'EUR',
    stripeToken: paymentToken.details.id,
    description: `Payment by ${customerEmail}`,
    email: customerEmail
  }

  console.group('store/bookings/actions/processPayment')
  console.info('Sending data to pre-authorize payment...')
  console.log(chargeData)

  try {
    // [Mock - Example]
    const data = {
      data: {
        id: 'ch_1FKkCR2eZvKYlo2CgqNRhtYl'
      }
    }

    // [REST-Example]
    // const data = await axios.post(endpoint, chargeData)

    console.info('Pre-authorized payment response...')
    console.dir(data)

    const {
      data: {
        id: chargeId
      }
    } = data

    console.log(chargeId)
    console.groupEnd()

    return chargeId
  } catch (err) {
    console.error(err)
    console.groupEnd()
    throw err
  }
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
 * @example
 *   const {
 *   // @ts-ignore
 *     data: {
 *      processBooking: { id: bookingProcessId }
 *     }
 *   } = await API.graphql(
 *     graphqlOperation(processBookingMutation, processBookingInput)
 *   );
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

    // const processBookingMutation = `mutation ProcessBooking($input: CreateBookingInput!) {
    //   processBooking(input: $input) {
    //     id
    //   }
    // }`

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

    // const {
    //   data: {
    //     data: { processBookingMutation: { id: bookingProcessId }
    //   }
    // } = result

    // [REST-Example]
    // const data = await axios({
    //   url: bookingEndpoint + '/bookings',
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
    console.error(err)
    console.groupEnd()
    throw err
  }
}
