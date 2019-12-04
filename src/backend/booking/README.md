
Booking service provides a GraphQL API for reservation, confirmation and cancellation operations.

## Implementation

![Booking Infrastructure Architecture](../../../media/booking-infra-architecture.png)

Booking is comprised of GraphQL API implemented using AppSync, DynamoDB as a database, a booking state machine using Step Functions and Python Lambda functions.

### GraphQL API

Booking API provides create, update, read and list (CRUD) operations on Bookings. It also enforces fine-grained authorization to allow booking owners to read and update their bookings only except Admin users.

#### Configuration

CRUD operations are auto-generated using Amplify off our [API schema](../../../amplify/backend/api/awsserverlessairline/schema.graphql). 

Operation | Name | Description
------------------------------------------------- | ---------------------- | --------------------------------------------------------------------
query | getBookingByStatus | Fetches bookings directly from Booking DynamoDB table
mutation | processBooking | Initiates booking state machine in Step Functions

These auto-generated operations are not currently being used and might change with [upcoming improvements](https://github.com/aws-samples/aws-serverless-airline-booking/projects/3). `getBooking`, `listBookings`, `createBooking`, `updateBooking`, `deleteBooking`. 

	
```graphql
type Booking 
    @model(subscriptions: null) 
    @auth(rules: [
      {allow: owner, ownerField: "customer", identityField: "sub", operations: [read, update]},
      {allow: groups, groups: ["Admin"]}
    ])
    @key(name: "ByCustomerStatus", 
        fields: ["customer", "status"],
        queryField: "getBookingByStatus")
{
    id: ID!
    status: BookingStatus!
    outboundFlight: Flight! @connection
    paymentToken: String!
    checkedIn: Boolean
    customer: String
    createdAt: String
    bookingReference: String
}
```

#### Operations

Access Logs and Server-side caching are not currently being used to prevent additional charges. When Access Logs is enabled, [you can use CloudWatch Log Insights to search across fully structured logs on all GraphQL API operations](https://aws.amazon.com/blogs/mobile/getting-more-visibility-into-graphql-performance-with-aws-appsync-logs/), including resolver and data statistics. 

### Booking state machine

TBW

#### Configuration

TBW

#### Operations

Both functions have X-Ray enabled and basic instrumentation, no custom subsegments or annotations yet. No custom metrics or structured logging at this point too.

## Integrations

### Front-end

TBW

### Payment

See [Payment integration section for more information](../payment/README.md)

### Decisions log

TBW