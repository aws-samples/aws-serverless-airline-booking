import Loyalty from "../../shared/models/LoyaltyClass";
import axios from "axios";
// @ts-ignore
import { Loading } from "quasar";

/**
 * Loyalty [Vuex Module Action](https://vuex.vuejs.org/guide/actions.html) - fetchLoyalty retrieves current authenticated user loyalty info from Loyalty service.
 *
 * It uses SET_LOYALTY mutation to update Loyalty state with the latest information.
 *
 * It also uses Quasar Loading spinner when fetching data from Loyalty service.
 * @param {object} context - Vuex action context (context.commit, context.getters, context.state, context.dispatch)
 * @param {object} context.commit - Vuex mutation function (context.commit)
 * @returns {promise} - Promise representing updated whether loyalty information has been updated in the store
 * @see {@link SET_LOYALTY} for more info on mutation
 * @example
 * // exerpt from src/views/Profile.vuw
 * async mounted() {
 *    if (this.isAuthenticated) {
 *        await this.$store.dispatch("loyalty/fetchLoyalty");
 *    }
 * }
 */
export function fetchLoyalty({ commit }) {
  return new Promise(async (resolve, reject) => {
    Loading.show({
      message: "Loading profile..."
    });

    try {
      const { data: loyaltyData } = await axios.get("/mocks/loyalty.json");
      const loyalty = new Loyalty(loyaltyData);

      commit("SET_LOYALTY", loyalty);

      Loading.hide();
      resolve();
    } catch (err) {
      Loading.hide();
      reject(err);
    }
  });
}
