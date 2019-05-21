
##########################
# Bootstrapping variables
##########################

target:
	$(info ${HELP_MESSAGE})
	@exit 0

init: ##=> Install OS deps, python3.6 and dev tools
	$(info [*] Bootstrapping CI system...)
	@$(MAKE) _install_os_packages

deploy: ##=> Deploy services
	$(info [*] Deploying...)
	$(MAKE) deploy.booking

deploy.booking: ##=> Deploy booking service using SAM
	$(info [*] Packaging and deploying Booking service...)
	cd src/backend/booking && \
		sam package \
			--s3-bucket $${DEPLOYMENT_BUCKET_NAME} \
			--region $${AWS_REGION} \
			--output-template-file packaged.yaml && \
		sam deploy \
			--template-file packaged.yaml \
			--stack-name $${STACK_NAME}-booking-$${AWS_BRANCH} \
			--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
			--parameter-overrides BookingTable=$${BOOKING_TABLE_NAME} FlightTable=$${FLIGHT_TABLE_NAME} \
			--region $${AWS_REGION}


#############
#  Helpers  #
#############

_install_os_packages:
	$(info [*] Installing Python and OS deps...)
	yum install jq python36 python36-devel python36-pip gcc glibc-headers -y
	$(info [*] Upgrading Python PIP...)
	python36 -m pip install --upgrade pip
	$(info [*] Installing SAM CLI and other tools...)
	python36 -m pip install cfn-lint aws-sam-cli

define HELP_MESSAGE
	Common usage:

	...::: Bootstraps environment with necessary tools like SAM and Pipenv :::...
	$ make init

	...::: Deploy all SAM based services :::...
	$ make deploy
endef
