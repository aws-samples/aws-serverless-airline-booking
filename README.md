# Frontend

## Deployment
1. In a seperated AWS account from the teams, create a x86 EC2 instance using Amazon Linux 2
	1. You can use SSM instead of SSH if you want.
	1. Security groups don't really matter here
1. You'll need to create an IAM user with the `AdministratorAccess-Amplify` policy
	1. Store the Access Key and Secret Key for later
1. Connect to the EC2 instance using SSM/SSH
1. Download whatever the latest version of NodeJS is from `https://nodejs.org/dist/latest-v16.x`
	1. `curl -L -O https://nodejs.org/dist/latest-v16.x/node-v16.18.1-linux-x64.tar.gz`
	1. `tar zxf node-v16.18.1-linux-x64.tar.gz`
	1. `export PATH=$PATH:$HOME/node-v16.18.1-linux-x64/bin`
1. Install `git`
	1. `yum install -y git`
1. Clone the Airline repo
	1. `git clone https://github.com/aws-samples/aws-serverless-airline-booking.git airline`
	1. `cd airline`
	1. `git checkout workshop`
1. Install Amplify CLI
	1. `npm i -g @aws-amplify/cli`
1. Configure Amplify, it'll ask a few questions
	1. `amplify init`
	1. Create a new environment (name it something other than 'dev')
	1. Choose an editor (none is a good idea)
	1. Select an auth method for amplify (AWS access keys)
		1. Enter the IAM secrets from earlier
		1. Enter a region (eu-west-1 works for EMEA really well)
	1. Let it complete
1. Install NPM deps for the frontend, this takes a while
	1. `npm i`
1. Add amplify hosting
	1. `amplify hosting add`
1. Publish the frontend`
	1. `amplify publish`
	1. It'll give you the environment URL to access the frontend in the output if all goes well.

## Updating endpoints
During the course of the workshop, you'll need to update parts of the codebase to ensure the teams can see their service working.
The updates are pretty trivial, they mostly involve changing the HTTP endpoint for their API.

### Booking Service
Change https://github.com/aws-samples/aws-serverless-airline-booking/blob/workshop/src/store/bookings/actions.js#L71

### Catalog
Change https://github.com/aws-samples/aws-serverless-airline-booking/blob/workshop/src/store/catalog/actions.js#LL96

### Loyalty
Change https://github.com/aws-samples/aws-serverless-airline-booking/blob/workshop/src/store/loyalty/actions.js#L40

### Payments
Change https://github.com/aws-samples/aws-serverless-airline-booking/blob/workshop/src/store/bookings/payment.js#L49

You also need to add a Stripe API key in the frontend here: https://github.com/aws-samples/aws-serverless-airline-booking/blob/workshop/src/pages/FlightSelection.vue#LL227
