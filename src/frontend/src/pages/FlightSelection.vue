<template>
  <q-page>
    <flight-toolbar
      v-if="this.selectedFlight"
      :departure="this.selectedFlight.departureAirportCode"
      :arrival="this.selectedFlight.arrivalAirportCode"
      :date="this.selectedFlight.departureDate"
    />
    <div class="flights">
      <div class="heading">
        <div
          class="text-h5 text-primary text-center flight__headline"
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
          class="form__header q-pt-md text-h5 text-primary text-center"
          data-test="form-header"
        >
          Payment details
        </div>
        <div class="form items-baseline">
          <form>
            <input type="hidden" name="token" />
            <div class="group">
              <label for="name">
                <span class="text-secondary">Name</span>
                <input
                  v-model="form.name"
                  id="name"
                  name="name"
                  placeholder="Name on card"
                  class="form__input field form__name"
                  data-test="form-name"
                  required
                />
              </label>
              <label>
                <span class="text-secondary">Country</span>
                <div class="form__payment--country field">
                  <q-select
                    v-model="form.country"
                    class="form__input form__input--select form__country"
                    @filter="filterFn"
                    :options="form.countryOptions"
                    option-value="label"
                    borderless
                    use-input
                    fill-input
                    data-test="form-country"
                    clearable
                    hide-selected
                    behaviour="menu"
                    item-aligned
                    emit-value
                  >
                    <template v-slot:option="scope">
                      <q-item v-bind="scope.itemProps" v-on="scope.itemEvents">
                        <q-item-section avatar>
                          <q-icon name="location_on" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label
                            class="text-subtitle1 search__options--suggestion"
                            >{{ scope.opt.label }} ({{
                              scope.opt.value
                            }})</q-item-label
                          >
                        </q-item-section>
                      </q-item>
                    </template>
                  </q-select>
                </div>
              </label>
              <label for="postcode">
                <span class="text-secondary">Postcode</span>
                <input
                  v-model="form.postcode"
                  id="postcode"
                  name="postcode"
                  placeholder="Postcode"
                  class="form__input field form__postcode"
                  data-test="form-postcode"
                  required
                />
              </label>
              <label>
                <span class="text-secondary">Card number</span>
                <div
                  id="card-number-element"
                  class="form__stripe field form__card"
                ></div>
              </label>
              <label>
                <span class="text-secondary">Expiry date</span>
                <div
                  id="card-expiry-element"
                  class="form__stripe field form__expiry"
                ></div>
              </label>
              <label>
                <span class="text-secondary">CVC</span>
                <div
                  id="card-cvc-element"
                  class="form__stripe field form__cvc"
                ></div>
              </label>
            </div>
            <div class="outcome">
              <div
                class="error text-bold text-secondary form__error"
                data-test="form-error"
                v-if="token.error"
              >
                {{ token.error.message }}
              </div>
            </div>
          </form>
        </div>
        <q-btn
          @click="payment"
          class="cta__button text-weight-medium"
          color="secondary"
          label="Book flight"
          :disable="$v.form.$invalid || form.isCardInvalid"
          data-test="payment-button"
        >
        </q-btn>
      </div>
    </div>
  </q-page>
</template>

<script>
// @ts-nocheck
import FlightCard from '../components/FlightCard'
import FlightToolbar from '../components/FlightToolbar'
import FlightClass from '../shared/models/FlightClass'
import FlightLoader from '../components/FlightLoader'
import { validationMixin } from 'vuelidate'
import { required, minLength } from 'vuelidate/lib/validators'
import { mapState, mapGetters } from 'vuex'
import { Logger } from '@aws-amplify/core'
import { Loading } from 'quasar'

const logger = new Logger('FlightSelection')
const countryList = [
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
]

var stripe, card

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
        required,
        minLength: minLength(3)
      }
    }
  },
  /**
   * @param {boolean} isAuthenticated - Getter from Profile module
   * @param {boolean} loading - Loader state used to control Flight Loader when fetching flights
   */
  computed: {
    ...mapGetters({
      firstName: 'profile/firstName',
      customer: 'profile/userAttributes',
      isAuthenticated: 'profile/isAuthenticated'
    }),
    ...mapState({
      loading: (state) => state.catalog.loading
    })
  },
  async beforeMount() {
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
        )
      }
    }
  },
  mounted() {
    /**
     * Stripe JS is loaded into the DOM asynchronously
     * once loaded we attach Stripe Elements to custom DOM elements
     * that makes payment credit card collection seamless through iFrame while providing an unified experience
     */
    this.loadStripeElements()
  },
  /**
   * @param {object} token - Stripe JS token object
   * @param {object} token.details - Stripe JS tokenized details
   * @param {object} token.error - Stripe JS error when attempting tokenization
   * @param {string} stripeKey - Public Stripe JS key for tokenization
   * @param {object} form - Form object holding some information and validation hooks
   * @param {string} form.name - Given contact name
   * @param {string} form.country - Given contact country
   * @param {object} form.countryOptions - List of countries we accept payment from
   * @param {boolean} isCardInvalid - Boolean updated through Stripe Elements events upon input
   * @param {Flight} selectedFlight - Selected Flight
   */
  data() {
    return {
      token: {
        details: '',
        error: ''
      },
      stripeKey:
        process.env.StripePublicKey ||
        process.env.VUE_APP_StripePublicKey ||
        'no Stripe public key',
      form: {
        name: '',
        country: '',
        postcode: '',
        countryOptions: countryList,
        isCardInvalid: true
      },
      selectedFlight: this.flight
    }
  },
  methods: {
    /**
     * Tokenize form and credit card data, and make charge request against Payment service
     * Given a successful payment it attempts to create a booking with Booking service
     * If booking completes successfuly, it redirects the customer to the Bookings view
     */
    async payment() {
      let options = {
        name: this.form.name,
        address_zip: this.form.postcode,
        address_country: this.form.country
      }

      try {
        const { token, error } = await stripe.createToken(card, options)
        this.token.details = token
        this.token.error = error

        if (this.token.error) throw this.token.error

        await this.$store.dispatch('bookings/createBooking', {
          paymentToken: this.token,
          outboundFlight: this.selectedFlight
        })

        // eslint-disable-next-line
        Loading.show({
          message: `Your booking is being processed - We'll soon contact you via ${this.customer.email}.`
        })
        setTimeout(() => {
          Loading.hide()
          this.$router.push({ name: 'bookings' })
        }, 3000)
      } catch (err) {
        logger.error('Error while creating a new booking: ', err)
        Loading.hide()
        this.$q.notify(
          `Error while creating your Booking - Check browser console messages`
        )
      }
    },
    /**
     * Provides customer feedback upon Stripe Elements card data validation
     */
    filterFn(val, update) {
      if (val === '' || val.length < 2) {
        update(() => {
          this.form.countryOptions = countryList
        })
        return
      }

      update(
        () => {
          const needle = val.toLowerCase()
          this.form.countryOptions = countryList.filter(
            (v) => v.label.toLowerCase().indexOf(needle) !== -1
          )
        },
        (ref) => {
          // auto-select first option
          if (val !== '' && ref.options.length > 0 && ref.optionIndex === -1) {
            ref.moveOptionSelection(1, true)
            ref.toggleOption(ref.options[ref.optionIndex], true)
          }
        }
      )
    },
    updateCardFeedback(result) {
      this.token.error = result.error
      this.form.isCardInvalid = !result.complete
    },
    /**
     * Once Stripe JS is loaded it attaches Stripe Elements to existing DOM elements
     * It also customizes Stripe Elements UI to provide a consistent experience
     */
    loadStripeElements() {
      stripe = Stripe(this.stripeKey) // eslint-disable-line
      let elements = stripe.elements()
      let style = {
        base: {
          iconColor: '#666EE8',
          color: '#31325F',
          lineHeight: '40px',
          fontWeight: 300,
          fontFamily: 'Helvetica Neue',
          fontSize: '15px',

          '::placeholder': {
            color: '#CFD7E0'
          }
        }
      }

      card = elements.create('cardNumber', {
        style: style
      })

      var cardExpiryElement = elements.create('cardExpiry', {
        style: style
      })

      var cardCvcElement = elements.create('cardCvc', {
        style: style
      })

      // Enable Stripe iFrame on each field
      card.mount('#card-number-element')
      cardExpiryElement.mount('#card-expiry-element')
      cardCvcElement.mount('#card-cvc-element')

      // Stripe Elements emit events upon card validation
      // Capture it and provide feedback to customer
      card.on('change', (event) => this.updateCardFeedback(event))
      cardExpiryElement.on('change', (event) => this.updateCardFeedback(event))
      cardCvcElement.on('change', (event) => this.updateCardFeedback(event))
    }
  }
}
</script>

<style lang="sass" scoped>
@import '../css/app'

.text-h5
  margin-top: 2rem

form
  width: auto
  margin: 20px

.group
  background: white
  box-shadow: 0 7px 14px 0 rgba(49, 49, 93, 0.1), 0 3px 6px 0 rgba(0, 0, 0, 0.08)
  border-radius: 4px
  margin-bottom: 20px

label
  position: relative
  font-weight: 300
  height: 40px
  line-height: 40px
  display: flex

.group label:not(:last-child)
  border-bottom: 1px solid #F0F5FA

label > span
  width: 120px
  text-align: right
  margin-right: 0.8rem
  margin-left: 0.6rem
  font-size: 1rem !important
  @media only screen and (min-device-width : 360px) and (max-device-width : 667px)
    width: 27vw
  @media (max-device-width: 360px)
    font-size: 0.99rem !important


.field
  min-width: 200px
  background: transparent
  font-weight: 300
  border: none
  color: #31325F
  outline: none
  flex: 1
  padding-right: 10px
  cursor: text
  font-size: 16px
  @media only screen and (min-device-width : 360px) and (max-device-width : 667px)
    padding-right: 0
    padding-left: 1px
  @media (max-device-width: 360px)
    padding-left: 5px
    padding-right: 5px

.field::-webkit-input-placeholder
  color: #CFD7E0
  font-weight: 700

.field::-moz-placeholder
  color: #CFD7E0
  font-weight: 700
  font-size: 16px

::placeholder,
.q-placeholder::placeholder
  color: #CFD7E0 !important
  font-size: 16px
  font-weight: 400 !important
  opacity: 1 !important
  position: relative

.outcome
  float: left
  width: 100%
  padding-top: 8px
  min-height: 24px
  text-align: center

.error
  font-size: 20px

.error.visible
  display: inline

.separator
  box-shadow: 0 7px 14px 0 rgba(49, 49, 93, 0.1), 0 3px 6px 0 rgba(0, 0, 0, 0.08)

.loader
  width: 150%

.cta__button
  width: 90%

.form__input
  padding: 3px
</style>
