

> **NOTICE**: AWS AppSync is not part of [Free tier](https://aws.amazon.com/free) and some AWS services used may not be covered by the [Free tier](https://aws.amazon.com/free) after 12 months.

## Requirements

Before you deploy, you must have the following in place:

* [AWS Account](https://aws.amazon.com/account/)
* [GitHub Account](https://github.com)
* [Node 10 or greater](https://nodejs.org/en/download/)
* [Amplify CLI 4.13.1 or greater installed and configured](https://aws-amplify.github.io/docs/cli-toolchain/quickstart#quickstart)
* [Stripe Account](https://dashboard.stripe.com/register)
    - Take note of your testing `Secret Key` and `Public Key` [located in the Stripe Dashboard](https://support.stripe.com/questions/locate-api-keys)

For prototyping, you need the following:

* [Python 3.7 or greater](https://realpython.com/installing-python/)
* [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Docker](https://docs.docker.com/install/)

## Howto

Follow these instructions to deploy the Serverless Airline application:

[![One-click deployment](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy?repo=https://github.com/aws-samples/aws-serverless-airline-booking)

1) Use **1-click deployment** button above
2) Expand `environment variables` and add your Stripe's keys
    - `STRIPE_PUBLIC_KEY`
    - `STRIPE_SECRET_KEY`
3) If you don't have an IAM Service Role, create one
4) Amplify Console forked this repository in your GitHub account, **clone your fork repo locally**
5) Within your new app in Amplify Console, wait for deployment to complete (this may take a while)
6) Choose **Backend environments**, and select the environment you see
7) Under **Edit backend**, copy the `amplify pull` command displayed
8) Within your forked repository locally, run the command you copied and follow the instructions
    - This command synchronizes what's deployed to your local Amplify environment

Within Amplify Console, you should see an auto-generated URL under **Frontend environment** - You can now sign-up for a new user, and add your first flight

> **NOTE**: We're currently working on an ETL feature to automatically add flights as part of CI.

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
