<template>
  <q-dialog @hide="onDialogHide" ref="dialog">
    <q-card style="width: 300px">
      <q-card-section class="filter__toolbar q-pa-none">
        <div class="row items-baseline filter__toolbar--header q-pa-sm">
          <div class="text-subtitle1 text-white col">Filters</div>
          <div class="text-subtitle1 text-right text-white col">
            <q-btn
              no-caps
              class="text-white"
              dense
              flat
              text-color="primary"
              size="0.90rem"
              label="Reset"
              padding="0"
              @click="resetFilters"
            />
          </div>
        </div>
        <div class="row items-baseline filter__toolbar--subheader q-pa-sm text">
          <div class="text-caption col">Results [filtered/total]</div>
          <div class="text-right col">
            <q-btn
              class="text-bold"
              no-caps
              dense
              flat
              text-color="primary"
              size="0.90rem"
              label="Apply"
              padding="0"
              @click="triggerFilters"
            />
          </div>
        </div>
      </q-card-section>

      <q-item-label header class="text-center q-pb-none text-primary"
        >Price range
      </q-item-label>
      <div class="q-px-lg q-py-md pricing__range">
        <div
          class="
            col-12
            pricing__range--content
            shadow-up-3
            bg-white
            row
            text-center
          "
        >
          <div class="col-6">
            <q-select
              v-model="priceFilter.min"
              class="pricing_minimum"
              color="primary"
              :options="pricingOptions"
              borderless
              dense
              hide-dropdown-icon
              hide-bottom-space
              item-aligned
              input-class="pricing__range--input"
            >
              <template v-slot:before>
                <span
                  class="
                    text-left text-subtitle2
                    filter__option--before
                    q-pl-xs
                  "
                  >from:</span
                >
              </template>
              <template v-slot:selected>
                <div class="text-bold filter__option--value text-subtitle2">
                  {{ priceFilter.min }}
                </div>
              </template>
            </q-select>
          </div>
          <div class="col-6 pricing__max">
            <q-select
              v-model="priceFilter.max"
              class="pricing_maximum"
              color="primary"
              :options="pricingOptions"
              borderless
              dense
              hide-dropdown-icon
              hide-bottom-space
              item-aligned
              input-class="pricing__range--input"
            >
              <template v-slot:before>
                <span
                  class="
                    text-left text-subtitle2
                    filter__option--before
                    text-dark
                    q-pl-md
                  "
                  >until:</span
                >
              </template>
              <template v-slot:selected>
                <div class="text-bold filter__option--value text-subtitle2">
                  {{ priceFilter.max }}
                </div>
              </template>
            </q-select>
          </div>
        </div>
      </div>
      <q-separator />

      <q-item-label header class="text-center q-pb-none text-primary"
        >Departure window</q-item-label
      >
      <div class="q-px-lg q-py-md schedule__range">
        <div
          class="
            col-12
            schedule__range--content
            shadow-up-3
            bg-white
            row
            text-center
          "
        >
          <div class="col-6">
            <q-field class="departure__earliest" borderless stack-label>
              <template v-slot:control>
                <q-popup-proxy>
                  <div>
                    <q-time
                      class="text-center"
                      v-model="departureFilter.min"
                      now-btn
                    >
                      <q-btn label="Close" flat color="primary" v-close-popup />
                    </q-time>
                  </div>
                </q-popup-proxy>
                <span class="full-width text-center text-subtitle2"
                  >earliest:
                  <span
                    class="
                      text-bold
                      filter__option--value
                      departure__earliest--value
                      cursor-pointer
                    "
                    >{{ departureFilter.min }}
                  </span>
                </span>
              </template>
            </q-field>
          </div>
          <div class="col-6 departure__max">
            <q-field class="departure__latest" borderless stack-label>
              <template v-slot:control>
                <q-popup-proxy>
                  <div>
                    <q-time
                      class="text-center"
                      v-model="departureFilter.max"
                      now-btn
                    >
                      <q-btn label="Close" flat color="primary" v-close-popup />
                    </q-time>
                  </div>
                </q-popup-proxy>
                <span class="full-width text-center text-subtitle2"
                  >latest:
                  <span
                    class="
                      text-bold
                      filter__option--value
                      departure__latest--value
                      cursor-pointer
                    "
                    >{{ departureFilter.max }}
                  </span>
                </span>
              </template>
            </q-field>
          </div>
        </div>
      </div>
      <q-separator />
      <q-item-label header class="text-center q-pb-none text-primary"
        >Arrival window</q-item-label
      >
      <div class="q-px-lg q-py-md schedule__range">
        <div
          class="
            col-12
            schedule__range--content
            shadow-up-3
            bg-white
            row
            text-center
          "
        >
          <div class="col-6">
            <q-field class="arrival__earliest" borderless stack-label>
              <template v-slot:control>
                <q-popup-proxy>
                  <div>
                    <q-time
                      class="text-center"
                      v-model="arrivalFilter.min"
                      now-btn
                    >
                      <q-btn label="Close" flat color="primary" v-close-popup />
                    </q-time>
                  </div>
                </q-popup-proxy>
                <span class="full-width text-center text-subtitle2"
                  >earliest:
                  <span
                    class="
                      text-bold
                      filter__option--value
                      arrival__earliest--value
                      cursor-pointer
                    "
                    >{{ arrivalFilter.min }}
                  </span>
                </span>
              </template>
            </q-field>
          </div>
          <div class="col-6 arrival__max">
            <q-field class="arrival__latest" borderless stack-label>
              <template v-slot:control>
                <q-popup-proxy>
                  <div>
                    <q-time
                      class="text-center"
                      v-model="arrivalFilter.max"
                      now-btn
                    >
                      <q-btn label="Close" flat color="primary" v-close-popup />
                    </q-time>
                  </div>
                </q-popup-proxy>
                <span class="full-width text-center text-subtitle2"
                  >latest:
                  <span
                    class="
                      text-bold
                      filter__option--value
                      arrival__latest--value
                      cursor-pointer
                    "
                    >{{ arrivalFilter.max }}
                  </span>
                </span>
              </template>
            </q-field>
          </div>
        </div>
      </div>
    </q-card>
  </q-dialog>
</template>
<style lang="sass">
@import '../css/app'

.q-timeline__title
  font-size: 1rem !important
  margin-bottom: 1vh !important
</style>
<script>
// @ts-ignore
import { date } from 'quasar'
import { mapGetters } from 'vuex'
import { Logger } from '@aws-amplify/core'

const logger = new Logger('ToolbarFilters')
const defaults = Object.freeze({
  pricing: {
    min: 100,
    max: 1000
  },
  schedule: {
    min: '06:00',
    max: '23:00'
  }
})

export default {
  /**
   *
   * Flight Toolbar Filters component to refine flight results
   */
  name: 'FlightToolbarFilters',
  methods: {
    resetFilters: function () {
      logger.debug('Resetting filter values to default')
      this.departureFilter = {
        min: defaults.schedule.min,
        max: defaults.schedule.max
      }
      this.arrivalFilter = {
        min: defaults.schedule.min,
        max: defaults.schedule.max
      }
      this.priceFilter = {
        min: defaults.pricing.min,
        max: defaults.pricing.max
      }
    },
    /**
     * Trigger event to apply filters
     *
     * @event apply
     */
    triggerFilters: function () {
      logger.debug("Propagating 'apply' event to apply filters")
      this.$emit('apply', {
        pricing: this.priceFilter,
        departure: this.departureFilter,
        arrival: this.arrivalFilter
      })
    },
    // NOTE: These are mandatory methods for q-dialog
    // Display dialog
    show: function () {
      // @ts-ignore
      this.$refs.dialog.show()
    },
    // Emit hide to comply with Dialog interface
    onDialogHide() {
      this.$emit('hide')
    }
  },
  data() {
    return {
      departureFilter: {
        min: defaults.schedule.min,
        max: defaults.schedule.max
      },
      arrivalFilter: {
        min: defaults.schedule.min,
        max: defaults.schedule.max
      },
      priceFilter: {
        min: defaults.pricing.min,
        max: defaults.pricing.max
      }
    }
  },
  computed: {
    pricingOptions() {
      let range = Array(11)
        .fill()
        .map((_, i) => i * 100)

      range.shift()

      return range
    }
  }
}
</script>
