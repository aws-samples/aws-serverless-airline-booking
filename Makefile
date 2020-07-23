
##########################
# Bootstrapping variables
##########################

AWS_BRANCH ?= "dev"
FLIGHT_TABLE_NAME ?= "UNDEFINED"
STACK_NAME ?= "UNDEFINED"
DEPLOYMENT_BUCKET_NAME ?= "UNDEFINED"
GRAPHQL_API_ID ?= "UNDEFINED"
BOOKING_TABLE_NAME ?= "UNDEFINED"

target:
	$(info ${HELP_MESSAGE})
	@exit 0

init: ##=> Install OS deps and dev tools
	$(info [*] Bootstrapping CI system...)
	@$(MAKE) _install_os_packages

deploy: ##=> Deploy services
	$(info [*] Deploying...)
	$(MAKE) deploy.shared-lambda-layers
	$(MAKE) deploy.payment
	$(MAKE) deploy.booking
	$(MAKE) deploy.loyalty
## Enable the deploy.perftest if you need to deploy the performance test stack
#	$(MAKE) deploy.perftest 

delete: ##=> Delete services
	$(MAKE) delete.booking
	$(MAKE) delete.payment
	$(MAKE) delete.loyalty
	$(MAKE) delete.shared-lambda-layers
## Enable the delete.perftest if you need to delete the performance test stack
#	$(MAKE) delete.perftest

delete.booking: ##=> Delete booking service
	$(MAKE) -C src/backend/booking delete

delete.payment: ##=> Delete payment service
	$(MAKE) -C src/backend/payment delete

delete.loyalty: ##=> Delete booking service
	aws cloudformation delete-stack --stack-name $${STACK_NAME}-loyalty-$${AWS_BRANCH}

delete.perftest:
	cdk destroy $${PERF_TEST_STACK_NAME}

delete.shared-lambda-layers: ##=> Delete shared Lambda layers stack
	$(MAKE) -C src/backend/shared/libs delete

deploy.booking: ##=> Deploy booking service using SAM
	$(MAKE) -C src/backend/booking deploy

deploy.payment: ##=> Deploy payment service using SAM
	$(MAKE) -C src/backend/payment deploy

deploy.loyalty: ##=> Deploy loyalty service using SAM and TypeScript build
	$(info [*] Packaging and deploying Loyalty service...)
	cd src/backend/loyalty && \
		npm install && \
		npm run build && \
		sam package \
			--s3-bucket $${DEPLOYMENT_BUCKET_NAME} \
			--output-template-file packaged.yaml && \
		sam deploy \
			--template-file packaged.yaml \
			--stack-name $${STACK_NAME}-loyalty-$${AWS_BRANCH} \
			--capabilities CAPABILITY_IAM \
			--parameter-overrides \
				BookingSNSTopic=/$${AWS_BRANCH}/service/booking/messaging/bookingTopic \
				Stage=$${AWS_BRANCH} \
				AppsyncApiId=$${GRAPHQL_API_ID}

deploy.perftest: ##=> Deploying Gatling components for performance testing
	$(info [*] Deploying Gatling components for performance testing ...)
	cd src/perf-tests/perftest-stack-airline && \
		npm install && \
		npm run build && \
		cdk list && \
		cdk bootstrap && \
		cdk deploy $${PERF_TEST_STACK_NAME} --require-approval never

deploy.shared-lambda-layers: ##=> Deploy shared Lambda Layers using SAM
	$(MAKE) -C src/backend/shared/libs deploy

export.parameter:
	$(info [+] Adding new parameter named "${NAME}")
	aws ssm put-parameter \
		--name "$${NAME}" \
		--type "String" \
		--value "$${VALUE}" \
		--overwrite

#############
#  Helpers  #
#############

_install_os_packages:
	$(info [*] Installing jq...)
	yum install jq -y
	$(info [*] Upgrading Python SAM CLI and CloudFormation linter to the latest version...)
	python3 -m pip install --upgrade --user cfn-lint aws-sam-cli
	npm -g install aws-cdk

define HELP_MESSAGE

	Environment variables:

	These variables are automatically filled at CI time except STRIPE_SECRET_KEY
	If doing a dirty/individual/non-ci deployment locally you'd need them to be set

	AWS_BRANCH: "dev"
		Description: Feature branch name used as part of stacks name; added by Amplify Console by default
	FLIGHT_TABLE_NAME: "Flight-hnxochcn4vfdbgp6zaopgcxk2a-xray"
		Description: Flight Table name created by Amplify for Catalog service
	STACK_NAME: "awsserverlessairline-twitch-20190705130553"
		Description: Stack Name already deployed; used for dirty/individual deployment
	DEPLOYMENT_BUCKET_NAME: "a_valid_bucket_name"
		Description: S3 Bucket name used for deployment artifacts
	GRAPHQL_API_ID: "hnxochcn4vfdbgp6zaopgcxk2a"
		Description: AppSync GraphQL ID already deployed
	BOOKING_TABLE_NAME: "Booking-hnxochcn4vfdbgp6zaopgcxk2a-xray"
		Description: Flight Table name created by Amplify for Booking service
	STRIPE_SECRET_KEY: "sk-test-asdf..."
		Description: Stripe Private Secret Key generated in Stripe; manually added in Amplify Console Env Variables per App

	Common usage:

	...::: Bootstraps environment with necessary tools like SAM CLI, cfn-lint, etc. :::...
	$ make init

	...::: Deploy all SAM based services :::...
	$ make deploy

	...::: Delete all SAM based services :::...
	$ make delete

	...::: Export parameter and its value to System Manager Parameter Store :::...
	$ make export.parameter NAME="/env/service/amplify/api/id" VALUE="xzklsdio234"
endef
