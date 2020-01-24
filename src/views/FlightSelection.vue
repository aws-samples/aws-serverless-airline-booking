<template>
  <q-page>
    <flight-toolbar
      v-if="this.selectedFlight"
      :departure="this.selectedFlight.departureAirportCode"
      :arrival="this.selectedFlight.arrivalAirportCode"
    />
    <div class="flights">
      <div class="heading">
        <div
          class="q-headline text-primary text-center flight__headline"
          data-test="flight-headline"
        >
          Review your selection
        </div>
        <div class="loader" v-if="loading">
          <flight-loader></flight-loader>
        </div>
      </div>
      <flight-card v-if="this.selectedFlight" :details="this.selectedFlight" />
    </div>
    <div class="form__payment">
      <div class="text-center">
        <div
          class="form__header q-pt-md q-headline text-primary text-center"
          data-test="form-header"
        >
          Payment details
        </div>
        <div class="form">
          <form>
            <input type="hidden" name="token" />
            <div class="group">
              <label for="name">
                <span class="text-secondary">Name</span>
                  <q-input
                    placeholder="Name on card"
                    v-model="form.name"
                    class="form__input field form__name"
                    :error="$v.form.name.$error"
                    hide-underline
                    data-test="form-name"
                    no-parent-field
                    @blur="$v.form.name.$touch"
                    error-label="Name is invalid"
                  />
              </label>
              <label>
                <span class="text-secondary">Country</span>
                <div class="form__payment--country field">
                  <q-select
                    v-model="form.country"
                    class="q-pt-sm form__select form__country"
                    filter
                    filter-placeholder="Country"
                    placeholder="Country"
                    :options="form.countryOptions"
                    hide-underline
                    data-test="form-country"
                    @blur="$v.form.country.$touch"
                    error-label="Country is invalid"
                  />
                </div>
              </label>
              <label for="postcode">
                <span class="text-secondary">Postcode</span>
                  <q-input
                    placeholder="Address postcode"
                    v-model="form.postcode"
                    class="form__input field form__postcode"
                    :error="$v.form.postcode.$error"
                    hide-underline
                    data-test="form-postcode"
                    no-parent-field
                    @blur="$v.form.postcode.$touch"
                    error-label="Postcode is invalid"
                  />
              </label>
              <label>
                <span class="text-secondary">Card number</span>
                  <q-input
                    placeholder="1034 442 4040 5321"
                    v-model="form.cardNumber"
                    class="form__input field form__cardNumber"
                    :error="$v.form.cardNumber.$error"
                    hide-underline
                    data-test="form-cardNumber"
                    no-parent-field
                    @blur="$v.form.cardNumber.$touch"
                    error-label="Card number is invalid"
                    maxlength="16"
                  />
              </label>
              <label>
                <span class="text-secondary">Expire Month</span>
                <q-input
                    placeholder="1 (e.g. 1 for January)"
                    type="number"
                    v-model="form.cardExpireMonth"
                    class="form__input field form__cardExpireMonth"
                    :error="$v.form.cardExpireMonth.$error"
                    hide-underline
                    data-test="form-cardExpireMonth"
                    no-parent-field
                    min="1"
                    max="12"
                    maxlength="2"
                    @blur="$v.form.cardExpireMonth.$touch"
                    error-label="Card number is invalid"
                  />
              </label>
              <label>
                <span class="text-secondary">Expire Year</span>
                  <q-input
                    placeholder="2022"
                    type="number"
                    v-model="form.cardExpireYear"
                    class="form__input field form__cardExpireYear"
                    :error="$v.form.cardExpireYear.$error"
                    hide-underline
                    data-test="form-cardExpireYear"
                    no-parent-field
                    min="2020"
                    max="2100"
                    maxlength="4"
                    @blur="$v.form.cardExpireYear.$touch"
                    error-label="Card number is invalid"
                  />
              </label>
              <label>
                <span class="text-secondary">CVC</span>
                  <q-input
                    placeholder="1234"
                    v-model="form.cardCvc"
                    class="form__input field form__card"
                    :error="$v.form.cardCvc.$error"
                    type="password"
                    hide-underline
                    data-test="form-cardCvc"
                    no-parent-field
                    maxlength="4"
                    @blur="$v.form.cardCvc.$touch"
                    error-label="Card CVC is invalid"
                  />
              </label>
            </div>
          </form>
        </div>
        <q-btn
          @click="payment"
          class="cta__button text-weight-medium"
          color="secondary"
          label="Agree and pay now"
          data-test="payment-button"
          :disable="$v.form.$invalid"
        >
          <q-icon
            class="cta__button--direction"
            name="keyboard_arrow_right"
            size="2.6rem"
          />
        </q-btn>
      </div>
    </div>
  </q-page>
</template>

<script>
// @ts-nocheck
import FlightCard from '../components/FlightCard';
import FlightToolbar from '../components/FlightToolbar';
import FlightClass from '../shared/models/FlightClass';
import FlightLoader from '../components/FlightLoader';
import { validationMixin } from 'vuelidate';
import { required } from 'vuelidate/lib/validators';
import { mapState, mapGetters } from 'vuex';

/**
 *
 * Flight Selection view displays selected Flight chosen by customer in Flight Results view along with Payment procedure
 */
export default {
  name: 'FlightSelection',
  /**
   * @param {Flight} flight - Selected Flight
   * @param {string} flightId - Selected Flight Unique Identifier
   */
  props: {
    flight: { type: FlightClass },
    flightId: { type: String, required: true }
  },
  components: {
    FlightCard,
    FlightToolbar,
    FlightLoader
  },
  mixins: [validationMixin],
  validations: {
    form: {
      name: {
        required
      },
      country: {
        required
      },
      postcode: {
        required
      },
      cardNumber: {
        required
      },
      cardExpireMonth: {
        required
      },
      cardExpireYear: {
        required
      },
      cardCvc: {
        required
      }
    }
  },
  /**
   * @param {boolean} isAuthenticated - Getter from Profile module
   * @param {boolean} loading - Loader state used to control Flight Loader when fetching flights
   */
  computed: {
    ...mapGetters('profile', ['isAuthenticated', 'email']),
    ...mapState({
      loading: state => state.catalog.loading,
      customer: state => state.profile.user
    })
  },
  async beforeMount () {
    /** authentication guards prevent authenticated users to view Flights
     * however, the component doesn't stop from rendering asynchronously
     * this guarantees we attempt talking to Catalog service
     * if our authentication guards && profile module have an user in place
     */
    if (this.isAuthenticated) {
      if (!this.flight) {
        this.selectedFlight = await this.$store.dispatch(
          'catalog/fetchByFlightId',
          {
            flightId: this.flightId
          }
        );
      }
    }
  },
  /**
   * @param {object} form - Form object holding some information and validation hooks
   * @param {string} form.name - Given contact name
   * @param {string} form.country - Given contact country
   * @param {string} form.postCode - Given contact's postcode
   * @param {string} form.cardExpireMonth - Given card's month expiration
   * @param {string} form.cardExpireYear - Given card's year expiration
   * @param {string} form.cardExpireCvc - Given card's cvc expiration
   * @param {object} form.countryOptions - List of countries we accept payment from
   * @param {Flight} selectedFlight - Selected Flight
   */
  data () {
    return {
      form: {
        name: 'Demo',
        country: 'UK',
        postcode: 'EC1A 2FD',
        countryOptions: [
          {
            label: 'Brazil',
            value: 'BR'
          },
          {
            label: 'United Kingdom',
            value: 'UK'
          },
          {
            label: 'United States',
            value: 'US'
          }
        ],
        cardNumber: '1055 444 3032 4679',
        cardExpireMonth: 1,
        cardExpireYear: 2022,
        cardCvc: null
      },
      selectedFlight: this.flight
    };
  },
  methods: {
    /**
     * Tokenize form and credit card data, and make charge request against Payment service
     * Given a successful payment it attempts to create a booking with Booking service
     * If booking completes successfuly, it redirects the customer to the Bookings view
     */
    async payment () {
      this.$v.form.$touch()

      if (this.$v.form.$invalid) {
        this.$q.notify('Please make sure all fields are filled.')
        throw new Error('Form is invalid...', this.$v.form)
      }

      const paymentDetails = {
        name: this.form.name,
        address_country: this.form.country,
        address_postcode: this.form.postcode,
        card: {
          number: this.form.cardNumber,
          expireMonth: this.form.cardExpireMonth,
          expireYear: this.form.cardExpireYear,
          cvc: this.form.cardCvc
        }
      };

      try {
        console.log('Form details...')
        console.table(paymentDetails);

        await this.$store.dispatch('bookings/createBooking', {
          paymentDetails: paymentDetails,
          outboundFlight: this.selectedFlight
        })

        this.$q.loading.show({
          message: `Your booking is being processed - We'll soon contact you via ${this.email}.`
        })

        setTimeout(() => {
          this.$q.loading.hide()
          this.$router.push({ name: 'bookings' })
        }, 3000)
      } catch (err) {
        this.$q.loading.hide();
        this.$q.notify(`${err}`)
        console.error(err);
      }
    }
  }
};
</script>

<style lang="stylus" scoped>
@import '~variables'

.flights
  margin-top $content-toolbar-margin

.q-headline
  margin-top 2rem

.form__payment, .form__header
  background $grey-2

form
  width auto
  margin 20px

.group
  background white
  box-shadow 0 7px 14px 0 rgba(49, 49, 93, 0.1), 0 3px 6px 0 rgba(0, 0, 0, 0.08)
  border-radius 4px
  margin-bottom 20px

label
  position relative
  font-weight 300
  height 40px
  line-height 40px
  display flex

.group label:not(:last-child)
  border-bottom 1px solid #F0F5FA

label > span
  width 120px
  text-align right
  margin-right 0.4rem

.field
  background transparent
  font-weight 300
  border none
  color #31325F
  outline none
  flex 1
  padding-right 10px
  padding-left 10px
  cursor text

.field::-webkit-input-placeholder
  color #CFD7E0

.field::-moz-placeholder
  color #CFD7E0

.outcome
  float left
  width 100%
  padding-top 8px
  min-height 24px
  text-align center

.error
  font-size 20px

.error.visible
  display inline

.separator
  box-shadow 0 7px 14px 0 rgba(49, 49, 93, 0.1), 0 3px 6px 0 rgba(0, 0, 0, 0.08)

.loader
  width 150%

</style>
