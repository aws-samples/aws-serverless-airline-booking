
Catalog module uses Catalog GraphQL API to search flights.

![Front-end Catalog high-level architecture](../../../../media/frontend_modules_catalog.png)

## Module structure

File | Description
------------------------------------------------- | ---------------------------------------------------------------------------------
actions.js | Async communication with Catalog API e.g. `fetchFlights`
airports.json | List of valid airports for searching flights
graphql.js | Custom GraphQL queries and their selection set e.g. `getFlightBySchedule`
mutations.js | Flight state mutation e.g. `SET_FLIGHTS(flightsArray)`
state.js | Flight catalog state including loader and pagination e.g. `state.paginationToken`


## Fetching flights

Catalog module provides `fetchFlights` and `fetchByFlightId` to interact with Catalog API.

Method | View | Parameters | Model
------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------
fetchFlights | Search, FlightResults | date, departure, arrival, paginationToken | [FlightClass][1]
fetchByFlightId | FlightSelection | flightId | [FlightClass][1]


[1]: ../../shared/models/FlightClass.js
