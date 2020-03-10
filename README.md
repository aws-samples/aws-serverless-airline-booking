## AWS Serverless Airline Booking

Serverless Airline Booking is a complete web application that provides Flight Search, Payment, Booking and Loyalty points including end-to-end testing, GraphQL and CI/CD. This web application was the theme of [Build on Serverless Season 2 on AWS Twitch running from April 24th until August 7th](https://pages.awscloud.com/GLOBAL-devstrategy-OE-BuildOnServerless-2019-reg-event.html).

**This branch is read-only, and primarily represents what we discussed on Twitch** - For improvements and more up-to-date information check [Develop branch](https://github.com/aws-samples/aws-serverless-airline-booking/tree/develop) and [Boards](https://github.com/aws-samples/aws-serverless-airline-booking/projects).

![Serverless Airline Booking sample](./media/prototype-web.png)

## Episodes

List of episodes we ran last year:

* **[Episode 1 - Development and Auth setup](http://bit.ly/2EwIHSc)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/2)
* **[Episode 2 - Building the Catalog service](http://bit.ly/2VJZ1F6)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/3)
* **[Episode 3 - Building the Booking service Pt 1](http://bit.ly/2YSmDcF)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/11)
* **[Episode 4 - Building the Booking service Pt 1](http://bit.ly/2X5z1Fs)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/12)
* **[Episode 5 - Building the Loyalty service](http://bit.ly/2Z8XfiP)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/15)
* **[Episode 6 - Testing the Loyalty service](http://bit.ly/2Wy5f0d)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/15)
* **[Episode 7 - Catch Up/Recap](https://youtu.be/rWTHXuLiOvk)**
* **[Episode 8 - Integration and E2E Testing Pt 1](https://youtu.be/g99BohPWNyE)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/17)
* **[Episode 9 - Integration and E2E Testing Pt 1](https://youtu.be/QiNwNKx1KT0)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/17)
* **[Episode 10 - Optimising our Infrastructure Pt 1](https://www.twitch.tv/videos/457858667)**
    - [WIP Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/19)
* **[Episode 11 - Optimising our Infrastructure Pt 2](https://www.twitch.tv/videos/457907686)**
    - [WIP Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/19)
* **[Episode 12 - Gaining Observability Pt 1](https://www.twitch.tv/videos/457923264)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/27)
* **[Episode 13 - Gaining Observability Pt 2](https://www.twitch.tv/videos/471252879)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/27)
* **[Episode 14 - Bonus Episode - Load testing/Perf improvements](https://www.twitch.tv/videos/464384029)**
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/74)
    - [Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/99)
    - [WIP Pull request](https://github.com/aws-samples/aws-serverless-airline-booking/pull/81)

## Deployment

To get started with the Serverless Airline application, you can deploy into your AWS Account by following our [Get Started instructions](./docs/getting_started.md)

## Stack

Summary of what the stack looks like now including a picture with the core tech:

* **Front-end** - Vue.js as the core framework, Quasar for UI, Amplify for Auth UI component and AWS integration, and Stripe JS with Stripe Elements for card tokenization, validation, etc.
* **Data** - All data is modeled after GraphQL types and stored in DynamoDB. Python being the core language for all services except Loyalty that's written in Typescript, and JavaScript for front-end.
* **API** - GraphQL is managed by AppSync and also acts as an API Hub to interact with other services. Loyalty implements a REST API to demonstrate how to secure service-to-service communication while maintaining a public endpoint. Payment API is also based on REST to demonstrate an external payment provider.
* **Auth** - Cognito provides JSON Web Tokens (JWT) and along with AppSync fine-grained authorization on what data types users can access.
* **Messaging** - Booking workflow is managed by Step Functions while SNS provides service-to-service communication through messaging between Booking and Loyalty.

![Core stack](./media/core-stack.png)

### Back-end

Back-end services that makes up the Serverless Airline functionalities as of now:

Service | Language | Description
------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------
[Catalog](./src/backend/catalog/README.md) | Apache VTL | Provides Flight search. CRUD operations including custom indexes are auto-generated by Amplify
[Booking](./src/backend/booking/README.md) | Python and Apache VTL | Provides new and list Bookings. CRUD operations including custom indexes are auto-generated by Amplify. Business workflow is implemented in Python.
[Payment](./src/backend/payment/README.md) | YAML and Python | Provides payment authorization, collection and refund. Bulk of Payment integration with Stripe is done via a [Serverless Application Repository App](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:375983427419:applications~api-lambda-stripe-charge). Payment collection and refund operations within Booking business workflow are in Python
[Loyalty](./src/backend/loyalty/README.md) | Typescript | Provides Loyalty points for customers including tiers. Fetching and ingesting Loyalty points are implemented in Typescript.

### Front-end

See more information about our [Front-end, components, routing and convention](./src/frontend/README.md)

**High level infrastructure architecture**

![Serverless Airline Architecture](./media/prototype-architecture.png)

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
