const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        alias: '/search',
        component: () => import('pages/Search.vue'),
        meta: { requiresAuth: true }
      },
      {
        name: 'searchResults',
        path: '/search/results',
        component: () => import('pages/FlightResults.vue'),
        props: (route) => ({ ...route.params, ...route.query }), // converts query strings and params to props
        meta: { requiresAuth: true }
      },
      {
        name: 'selectedFlight',
        path: '/search/results/review',
        component: () => import('pages/FlightSelection.vue'),
        props: (route) => ({ ...route.params, ...route.query }), // converts query strings and params to props
        meta: { requiresAuth: true }
      },
      {
        path: '/profile',
        name: 'profile',
        component: () => import('pages/Profile.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/profile/bookings',
        name: 'bookings',
        component: () => import('pages/Bookings.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/auth',
        name: 'auth',
        component: () => import('pages/Authentication.vue'),
        props: (route) => ({ ...route.params, ...route.query }) // converts query strings and params to props
      }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
