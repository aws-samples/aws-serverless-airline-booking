
Bookings module uses Bookings GraphQL API to fetch customer's bookings.

![Front-end Bookings high-level architecture](../../../../media/frontend_modules_bookings.png)

## Module structure

File | Description
------------------------------------------------- | ---------------------------------------------------------------------------------
actions.js | Async communication with Bookings API e.g. `fetchBooking`
graphql.js | Custom GraphQL queries and their selection set e.g. `GetBookingByStatus`
mutations.js | Bookings state mutation e.g. `SET_BOOKINGS(bookingData)`
payment.js | Process pre-authorization payment sync. with Payments API
state.js | Bookings state including pagination e.g. `state.bookings`

> **NOTE**: Payment will be integrated into the back-end schema, and calls will be made via GraphQL in the future for completeness. As of now, it doesn't require a separate module as it doesn't manipulate its own state.

## Fetching Bookings points

Bookings module provides `fetchBooking` and `createBooking` to interact with Bookings API.

Method | View | Parameters | Model
------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------
fetchBooking | Bookings | paginationToken, it uses authenticated user ID for booking owner | [BookingsClass][1]
createBooking | Bookings | outboundFlight, paginationToken, it uses authenticated user ID for booking owner | [BookingsClass][1]
processPayment | Bookings | paymentToken, outboundFlight, customerEmail | N/A

[1]: ../../shared/models/BookingClass.js
