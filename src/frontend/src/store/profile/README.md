
Profile module doesn't interact with our API but Amplify Auth library only.

## Module structure

File | Description
------------------------------------------------- | ---------------------------------------------------------------------------------
actions.js | Async communication with Amazon Cognito User Pools via Amplify e.g. `getSession`
getters.js | Getters for commonly used user data e.g. `firstName, isAuthenticated`
mutations.js | Profile state mutation e.g. `SET_USER(userSession)`
state.js | Profile state e.g. `state.user`

## Retrieving user session

User session is validated and retrieved within [routing Navigation Guard](../../README.md#Router). As customers successfully authenticates, this module hydrates its state so other components can check whether customers are authenticated before proceeding their responsibilities. 

Additionally, we listen for sign-out events within Profile View, and redirect to Authentication View.

Method | View | Parameters | Model
------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------
getSession | Profile | None | N/A

**Getters**

* `isAuthenticated `
* `firstName`
* `lastName`
* `userAttributes`

> **NOTE**: We might create a profile back-end service where this will become more meaningful.
