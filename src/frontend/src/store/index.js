import Vue from 'vue'
import Vuex from 'vuex'

// import example from './module-example'
import catalog from './catalog'
import profile from './profile'
import bookings from './bookings'
import loyalty from './loyalty'

Vue.use(Vuex)

const Store = new Vuex.Store({
  modules: {
    catalog,
    profile,
    bookings,
    loyalty
  },

  // enable strict mode (adds overhead!)
  // for dev mode only
  strict: process.env.DEBUGGING
})

export default Store
