<template>
  <div class="flight__options">
    <q-page-sticky expand position="top">
      <q-toolbar class="flight__filter--toolbar" color="grey-1">
        <q-toolbar-title class="text-dark text-weight-bold row">
          <div class="flight__orientation col-11 text-left">
            <span
              class="flight__departure--toolbar"
              data-test="toolbar-departure"
              >{{ departure }}</span
            >
            <q-btn flat round dense icon="swap_horiz" />
            <span
              class="flight__arrival--toolbar"
              data-test="toolbar-arrival"
              >{{ arrival }}</span
            >
          </div>
        </q-toolbar-title>
      </q-toolbar>
    </q-page-sticky>
  </div>
</template>

<script>
export default {
  /**
   *
   * Flight Toolbar component represents flight direction when searching/paying for a given flight
   *
   * @example
   *
   * const flight = new Flight(flightData)
   *
   * <flight-toolbar
   *  :departure="flight.departureAirportCode"
   *  :arrival="flight.arrivalAirportCode">
   * </flight-toolbar>
   */
  name: "FlightToolbar",
  props: {
    /**
     * @param {string} departure - Sets departure airport code (IATA)
     */
    departure: { type: String, required: true },
    /**
     * @param {string} arrival - Sets arrival airport code (IATA)
     */
    arrival: { type: String, required: true }
  }
};
</script>
