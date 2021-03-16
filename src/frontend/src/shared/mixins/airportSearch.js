import airports from '../../store/catalog/airports.json'
import Fuse from 'fuse.js'

/**
 * Airport suggestion
 * @typedef {Object} AirportSuggestion
 * @property {string} city - Airport's city
 * @property {string} name - Airport long name
 * @property {number} code - Airport IATA code
 */

/**
 * parse list of airports provided from Catalog module
 *
 * @return {AirportSuggestion[]} - list of airports following auto-suggestion Quasar component contract
 */
const parseAirports = () => {
  return airports.map((country) => {
    return {
      city: country.city,
      name: country.name,
      code: country.code
    }
  })
}

const fuzzySearchDefaults = {
  shouldSort: true,
  threshold: 0.3,
  location: 0,
  distance: 100,
  maxPatternLength: 10,
  minMatchCharLength: 3,
  keys: ['city', 'code', 'name']
}

export const airportList = parseAirports()
const fuse = new Fuse(airportList, fuzzySearchDefaults)

export const airportSearchMixin = {
  // ...
  data() {
    return {
      airportSearch_suggestionList: airportList
    }
  },
  methods: {
    /**
     * Q-Select Filter function
     * @name qSelectFn
     * @function
     * @link https://quasar.dev/vue-components/select#Filtering-and-autocomplete
     */

    /**
     * Quasar Select filter function triggered to autosuggest airports
     *
     * @param {string} value - Airport to be searched
     * @param {qSelectFn} update - Function to update list of autosuggestions
     * @param {qSelectFn} abort - Function to prevent any search, loaders, and autosuggestion behaviour
     */
    $airportSearch_fuzzySearch(value, update, abort) {
      // Min 3 chars for autocomplete
      if (value.length < 3) {
        abort()
        return
      }

      update(
        () => {
          // reset the list if search was cleared
          if (value === '') {
            this.airportSearch_suggestionList = airportList
          }

          let result = fuse.search(value.toLowerCase())
          this.airportSearch_suggestionList = result.map((i) => i.item)
        },
        // "ref" is the Vue reference to the QSelect
        (ref) => {
          if (value !== '' && ref.options.length > 0) {
            ref.setOptionIndex(-1) // reset optionIndex in case there is something selected
            ref.moveOptionSelection(1, true) // focus the first selectable option and do not update the input-value
          }
        }
      )
    }
  }
}
