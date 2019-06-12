import Vue from "vue";
import Vuex from "vuex";

import profile from "./store/profile";
import catalog from "./store/catalog";
import bookings from "./store/bookings";
import loyalty from "./store/loyalty";

Vue.use(Vuex);

const modules = {
  profile,
  catalog,
  bookings,
  loyalty
};

const store = new Vuex.Store({ modules });

export default store;
