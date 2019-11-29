## AWS Serverless Airline Booking

**STATUS**: Work-in-progress, ETA re:Invent 2019

Airline Booking is a complete web application that provides Flight Search, Flight Payment, Flight Booking, Flight Preferences and Loyalty points including end-to-end testing, GraphQL and CI/CD. This web application is the theme of [Build on Serverless Season 2 on AWS Twitch running from April 24th until August 7th](https://pages.awscloud.com/GLOBAL-devstrategy-OE-BuildOnServerless-2019-reg-event.html).

![Serverless Airline Booking sample](./media/prototype-web.png)

Table of Contents
=================

* [Deploying](#Deploying)
    - [Requirements](#Requirements)
    - [Instructions](#Instructions)
        + [Adding your first flight](#Adding-your-first-flight)
* [FAQ](#FAQ)

## Deploying

### Requirements

* [AWS Account](https://aws.amazon.com/account/)
* [Python 3.7 or greater](https://realpython.com/installing-python/)
* [Node 8.10 or greater](https://nodejs.org/en/download/)
* [Amplify CLI 1.12.0 or greater](https://aws-amplify.github.io/docs/cli-toolchain/quickstart#quickstart)
* [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Docker](https://docs.docker.com/install/)
* [Stripe Account](https://dashboard.stripe.com/register)
    - Take note of your testing `Secret Key` [located in the Stripe Dashboard](https://support.stripe.com/questions/locate-api-keys)

### Instructions

These are the deployment steps until the full implementation is complete.:

1) Fork this project and clone to your local laptop/cloud IDE
2) Locally, within your fork, run **`amplify init`**
3) Choose to create a new environment (i.e. dev)
4) Verify that you now have at least `Auth` and `Api` categories by running **`amplify status`**
5) Deploy amplify managed infrastructure by running **`amplify push`**
6) Once complete, open [AWS Amplify Console](https://eu-west-1.console.aws.amazon.com/amplify/home) and select **`Deploy`** if this is your first time using it
7) Click on `Connect app`, select `GitHub`, choose your Fork repo and select the branch **`develop`**
8) Under "Existing Amplify backend detected", **select your new environment** created in Step 2
9) Choose an existing Amplify Console or create a new one
10) Lastly, expand **Environment Variables**, and add **`STRIPE_SECRET_KEY`** and **`STRIPE_PUBLIC_KEY`** and its value, then conclude the installation

#### Adding your first flight

> NOTE: **This will no longer be necessary once ETL is merged to `develop` branch**

Firstly, we need a valid Cognito User that you can create by signing up within your new deployed front-end - Steps below will guide you to manually add your first flight into Catalog:

1. Within [Amplify Console](https://eu-west-1.console.aws.amazon.com/amplify/home), select your App, use the URL created to access the Front-end and **select Sign Up**
2. Once you confirm your user, take note of the value `aws_user_pools_web_client_id` inside `src/frontend/aws-exports.js`
3. Go to the [AWS AppSync Console](https://eu-west-1.console.aws.amazon.com/appsync/home), and select the `Serverless Airline API`
4. Go to `Queries` on the left menu, and select `Login with User Pools`
5. Within `ClientId` use the value you took note in `Step 2`, and use the credentials of your newly created Cognito user
6. Within your project, copy any of the `createFlight` mutations provided in **`sample-queries-mutations.gql`**
7. Open up the front-end, and search for a flight from **`LGW`** to **`MAD`** for **December 2nd, 2019**

---

## FAQ

**Q: Will the README be updated with more info?**

Yes! We'll make incremental changes as the series progress.

**Q: When will the full code be available?**

ETA is for re:Invent 2019. We've decided to spend more time polishing utility libraries, and bake more best practices. Expectation to call it complete will be when the following is fully implemented:

* [ ] Full suite of tests
* [ ] Migrate to Quasar 1.0 (now GA)
* [ ] Python and JS utility library for tracing, structured logging and async custom metrics
* [ ] Detailed README for each folder
* [ ] ETL to hydrate flights
* [ ] Major performance optimizations merged
* [ ] Performance Load test scenarios

**Q: Will episodes be recorded?**

Yes! You can find them in the [Landing Page]([Build on Serverless Season 2 on AWS Twitch running from April 24th until August 7th](https://pages.awscloud.com/GLOBAL-devstrategy-OE-BuildOnServerless-2019-reg-event.html) or as a [Twitch Collection](https://www.twitch.tv/collections/2s5GEfNTuRXCeg)

**Q: What are you using for the front-end?**

![Front-end tech stack](./media/prototype-frontend.png)

**Q: What is the high level infra architecture?**

![Serverless Airline Architecture](./media/prototype-architecture.png)

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
