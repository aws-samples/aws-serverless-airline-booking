import Vue from 'vue'
import VueRouter from 'vue-router'

import routes from './routes'
import store from '../store'

Vue.use(VueRouter)

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default function (/* { store, ssrContext } */) {
  const Router = new VueRouter({
    scrollBehavior: () => ({ x: 0, y: 0 }),
    routes,
    mode: process.env.VUE_ROUTER_MODE,
    base: process.env.VUE_ROUTER_BASE
  })

  /**
   * Authentication Guard for routes with requiresAuth metadata
   *
   * @param {Object} to - Intended route navigation
   * @param {Object} from - Previous route navigation
   * @param {Object} next - Next route navigation
   * @returns {Object} next - Next route
   */
  Router.beforeEach(async (to, from, next) => {
    const isProtected = to.matched.some((record) => record.meta.requiresAuth)
    if (isProtected) {
      console.info(`Page ${to.fullPath} requires Auth!`)
      if (!store.getters['profile/isAuthenticated']) {
        try {
          await store.dispatch('profile/getSession')
          next()
        } catch (err) {
          next({ name: 'auth', query: { redirectTo: to.name } })
        }
      }
    }
    next()
  })

  return Router
}
