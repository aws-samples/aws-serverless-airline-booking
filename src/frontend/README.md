
The front-end is built atop Vue.js, and uses Vuex modules to integrate with its back-ends - See [Stack details for completeness](../../README.md#Stack)

![Front-end high-level architecture](../../media/prototype-frontend.png)

## Modules

These are the Vuex modules that manipulate the state, and integrate with each back-end hosted at AWS:

Component | Functionality | Description
------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------
[Catalog](./store/catalog/README.md) | Flight search | Searches for flights given a destination and departure date.
[Booking](./store/booking/README.md) | Bookings | Creates and lists bookings for customers.
[Loyalty](./store/loyalty/README.md) | Loyalty | Fetches Loyalty points for customers including tiers, and calculates how far they are from the next tier.
[Profile](./store/profile/README.md) | Customer profile | Provides authenticated user information to other components such as JWT tokens (user attributes, etc.). It may be extended to create an actual profile service on the back-end.

## Components

We use `component` and `view` terminologies to separate what's a reusable Vue component, and what's a page that need to manipulate state within Vuex.

* **[FlightCard](./components/FlightCard.vue)** - Component to render a flight card when searching or reviewing flight results
* **[FlightLoader](./components/FlightLoader.vue)** - Custom content loader used when searching for flights
* **[FlightToolbar](./components/FlightToolbar.vue)** - Component to filter and sort flight results
* **[BookingCard](./components/BookingCard.vue)** - Component to render modal that provides more details about a booking
* **[BookingFlight](./components/BookingFlight.vue)** - Component to filter and sort flight results

## Views

`Views` map to pages customers interact with, and integrate with their respective modules to fetch and manipulate data from back-ends - [See more details for each view component](./views/README.md)

### Router

We use [Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html) to enforce authentication for routes that contain `requiresAuth` metadata.

Route | View | Query strings
-------------------------------------- | ------------------------------------------ | ------------------------------------------
/auth | Authentication | None
/, /search | Search | None
/search/results | FlightResults | date, departure, arrival
/search/results/review | FlightSelection | flightId
/profile | Profile | None
/profile/bookings | Bookings | None
