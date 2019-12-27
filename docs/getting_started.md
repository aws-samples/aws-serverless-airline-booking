

> **NOTICE**: AWS AppSync is not part of [Free tier](https://aws.amazon.com/free) and some AWS services used may not be covered by the [Free tier](https://aws.amazon.com/free) after 12 months.

## Requirements

Before you deploy, you must have the following in place:

* [AWS Account](https://aws.amazon.com/account/)
* [Python 3.7 or greater](https://realpython.com/installing-python/)
* [Node 8.10 or greater](https://nodejs.org/en/download/)
* [Amplify CLI 3.17.0 or greater installed and configured](https://aws-amplify.github.io/docs/cli-toolchain/quickstart#quickstart)
* [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Docker](https://docs.docker.com/install/)
* [Stripe Account](https://dashboard.stripe.com/register)
    - Take note of your testing `Secret Key` and `Public Key` [located in the Stripe Dashboard](https://support.stripe.com/questions/locate-api-keys)

## Howto

Follow these instructions to deploy the Serverless Airline application:

1) Fork this project and take note of the url
2) Within an empty directory, initialize the project with **``amplify init --app <fork-github-url>``**
3) Choose to create a new environment (i.e. dev)
4) Verify that you now have at least `Auth` and `Api` categories by running **`amplify status`**
5) Deploy amplify managed infrastructure by running **`amplify push`**
6) Once complete, open [AWS Amplify Console](https://console.aws.amazon.com/amplify/home)
    - If this is your first time using Amplify Console, select **`Deploy`**
7) Click on `Connect app`, select `GitHub`, choose your Fork repo and select the branch **`develop`**
8) Under "Existing Amplify backend detected", **select your new environment** created in Step 2
9) Choose an existing Amplify Console IAM Role or create a new one

At the end of the first deployment, you should have a new URL where you can visit and sign the first user up - Next steps being setup payment and add flights.

> **NOTE**: We're currently working on an ETL feature to automatically add flights as part of CI.

### Setting up Stripe integration

**Public key for tokenizing card data during flight booking**

1. Within your fork, open front-end environment variable file **`src/frontend/.env`**
2. Update the value of **`VUE_APP_StripePublicKey`** with your Stripe public key

**Secret key for collecting pre-authorized charges**

1. Within [AWS Amplify Console](https://console.aws.amazon.com/amplify/home), select your App and expand ``Environment Variables``
2. Add **`STRIPE_SECRET_KEY`** environment variable and its value


### Adding your first flight

Provided you have followed deployment instructions and signed up your first user, take the steps below to log in to AWS AppSync and run a `createFlight` mutation:

1. Open Amplify variable file **`src/frontend/aws-exports.js`** and take note of **`aws_user_pools_web_client_id`**
2. Go to the [AWS AppSync Console](https://console.aws.amazon.com/appsync/home), and select the `Serverless Airline API`
3. Go to `Queries` on the left menu, and select `Login with User Pools`
4. Within `ClientId` use the value you took note in `Step 1`, and use the credentials of your newly created Cognito user
5. Within your fork, copy any of the `createFlight` mutations provided in **`sample-queries-mutations.gql`**
6. Open up the front-end, and search for a flight from **`LGW`** to **`MAD`** for **December 2nd, 2019**

## Cleaning up

To delete the Serverless Airline from your AWS Account, you need: 

* **Git branch name** - Branch you connected in Amplify Console (e.g. twitch)
* **Root Stack name** - Root CloudFormation Stack name, available in System Manager Parameter Store (e.g. /twitch/stackName)

By running the commands below within the project source code, you will

1. Fetch the root stack name into STACK_NAME environment variable
2. Export the `git branch name` used in Amplify Console - **you need to replace with the correct value**
3. Delete all back-ends managed by Serverless Application Model (SAM) in the correct order
4. Delete all resources managed by Amplify (API, DynamoDB Table, Cognito)

```bash
# export AWS_BRANCH="twitch"
export AWS_BRANCH="<<Git Branch Name you used>>"
export STACK_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/deployment/stackName --query 'Parameter.Value' --output text)

make delete
amplify delete
```

Lastly, deployment S3 buckets may remain untouched. You can safely delete buckets starting with **`awsserverlessairline-<<<timestamp>>>-deployment`**, use either [via Console, CLI or SDK](https://docs.aws.amazon.com/AmazonS3/latest/dev/delete-or-empty-bucket.html#delete-bucket)
