import Booking from "../../shared/models/BookingClass";
import Flight from "../../shared/models/FlightClass";
// @ts-ignore
import { Loading } from "quasar";
import axios from "axios";

import { API, graphqlOperation } from "aws-amplify";
import {
  processBooking as processBookingMutation,
  listBookings
} from "./graphql";

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
export function fetchBooking({ commit }) {
  return new Promise(async (resolve, reject) => {
    Loading.show({
      message: "Loading bookings..."
    });

    try {
      // TODO: Fix Enum value passing
      // const bookingFilter = {
      //   filter: {
      //     status: {
      //       eq: "CONFIRMED"
      //     }
      //   }
      // };
      const {
        // @ts-ignore
        data: {
          listBookings: { items: bookingData }
        }
      } = await API.graphql(graphqlOperation(listBookings));

      let bookings = bookingData.map(booking => new Booking(booking));

      console.log(bookings);

      commit("SET_BOOKINGS", bookings);

      resolve();
      Loading.hide();
    } catch (err) {
      console.error(err);
      reject(err);
    }
  });
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
export async function createBooking(
  { rootState },
  { paymentToken, outboundFlight }
) {
  try {
    let paymentEndpoint = process.env.VUE_APP_PaymentChargeUrl;
    const customerEmail = rootState.profile.user.attributes.email;
    let chargeToken = await processPayment({
      endpoint: paymentEndpoint,
      paymentToken,
      outboundFlight,
      customerEmail
    });

    Loading.show({
      message: "Payment authorized successfully..."
    });

    let bookingProcessId = await processBooking({
      chargeToken,
      outboundFlight
    });

    return bookingProcessId;
  } catch (err) {
    throw err;
  }
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
async function processPayment({
  endpoint,
  paymentToken,
  outboundFlight,
  customerEmail
}) {
  Loading.show({
    message: "Charging a pre-authorization..."
  });

  if (!paymentToken) throw "Invalid payment token";

  const chargeData = {
    amount: outboundFlight.ticketPrice,
    currency: outboundFlight.ticketCurrency,
    stripeToken: paymentToken.details.id,
    description: `Payment by ${customerEmail}`,
    email: customerEmail
  };

  try {
    const data = await axios.post(endpoint, chargeData);
    const {
      data: {
        createdCharge: { id: chargeId }
      }
    } = data;

    return chargeId;
  } catch (err) {
    console.error(err);
    throw err;
  }
}

/**
 *
 * Process Booking function - processBooking uses processBooking mutation to kick off an async Booking Workflow that ultimatelly reserves flight seat, creates a booking reference, collect payment, etc.
 *
 * @param {object} obj - Object containing params to process payment
 * @param {string} obj.chargeToken - Pre-authorized payment token
 * @param {Flight} obj.outboundFlight - Outbound flight
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
async function processBooking({ chargeToken, outboundFlight }) {
  const processBookingInput = {
    input: {
      paymentToken: chargeToken,
      bookingOutboundFlightId: outboundFlight.id
    }
  };

  try {
    Loading.show({
      message: "Creating a new booking..."
    });

    const {
      // @ts-ignore
      data: {
        processBooking: { id: bookingProcessId }
      }
    } = await API.graphql(
      graphqlOperation(processBookingMutation, processBookingInput)
    );

    return bookingProcessId;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
