
Loyalty module uses Loyalty GraphQL API to fetch customer's loyalty details.

![Front-end Loyalty high-level architecture](../../../../media/frontend_modules_loyalty.png)

## Module structure

File | Description
------------------------------------------------- | ---------------------------------------------------------------------------------
actions.js | Async communication with Loyalty API e.g. `fetchLoyalty`
graphql.js | Custom GraphQL queries and their selection set e.g. `getLoyalty`
mutations.js | Loyalty state mutation e.g. `SET_LOYALTY(loyaltyData)`
state.js | Loyalty state e.g. `state.loyalty`


## Fetching loyalty points

Loyalty module provides `fetchLoyalty` to interact with Loyalty API.

Method | View | Parameters | Model
------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------
fetchLoyalty | Profile | None, it uses authenticated user ID | [LoyaltyClass][1]

[1]: ../../shared/models/LoyaltyClass.js
