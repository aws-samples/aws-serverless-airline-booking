import Booking from "../../shared/models/BookingClass";
import Flight from "../../shared/models/FlightClass";
// @ts-ignore
import { Loading } from "quasar";
import axios from "axios";

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
      const { data: bookingData } = await axios.get("/mocks/bookings.json");
      const bookings = bookingData.map(booking => new Booking(booking));
      bookings.map(booking => {
        booking.inboundFlight = new Flight(booking.inboundFlight);
        booking.outboundFlight = new Flight(booking.outboundFlight);

        return booking;
      });

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
 *              outboundFlight: this.flight
 *            });
 *        ...
 *        }
 */
export function createBooking(
  { commit },
  { paymentToken, outboundFlight, inboundFlight }
) {
  const processPayment = () => {
    Loading.show({
      message: "Processing payment..."
    });

    return new Promise((resolve, reject) => {
      if (!paymentToken) reject("Invalid payment token");

      setTimeout(() => {
        let response = {
          data: {
            createPayment: {
              token: paymentToken,
              status: "CONFIRMED"
            }
          }
        };
        resolve(response);
      }, 1000);
    });
  };

  const processBooking = () => {
    Loading.show({
      message: "Booking confirmed! Redirecting to Bookings"
    });

    return new Promise(resolve => {
      setTimeout(() => {
        let response = {
          data: {
            createBooking: {
              id: "FK1ZL18",
              departureCity: "London",
              transactionDate: new Date().toISOString(),
              inboundFlight: inboundFlight,
              outboundFlight: outboundFlight
            }
          }
        };
        resolve(response);
      }, 1000);
    });
  };

  return new Promise(async (resolve, reject) => {
    try {
      await processPayment();

      let {
        data: { createBooking: bookingData }
      } = await processBooking();
      let booking = new Booking(bookingData);
      resolve(booking);
    } catch (err) {
      reject(err);
    }
  });
}
