PROFILE := "twitch"
SHARED_LIBS_LAYER ?= "arn:aws:lambda:eu-west-1:231436140809:layer:SharedLibsLayer:12"

target:
	@$(MAKE) pr

dev:
	poetry install

format:
	poetry run isort -rc .
	poetry run black src
	poetry run black tests

lint: format
	poetry run flake8

test:
	poetry run pytest

test-html:
	poetry run pytest --cov-report html

pr: lint test

invoke-cancel-booking:
	sam local invoke \
		--event src/cancel-booking/event.json \
		--env-vars local-env-vars.json CancelBooking \
		--parameter-overrides SharedLibsLayer=${SHARED_LIBS_LAYER} \
		--profile ${PROFILE}

invoke-confirm-booking:
	sam local invoke \
		--event src/confirm-booking/event.json \
		--env-vars local-env-vars.json ConfirmBooking \
		--parameter-overrides SharedLibsLayer=${SHARED_LIBS_LAYER} \
		--profile ${PROFILE}

invoke-notify-booking:
	sam local invoke \
		--event src/notify-booking/event.json \
		--env-vars local-env-vars.json NotifyBooking \
		--parameter-overrides SharedLibsLayer=${SHARED_LIBS_LAYER} \
		--profile ${PROFILE}

invoke-reserve-booking:
	sam local invoke \
		--event src/reserve-booking/event.json \
		--env-vars local-env-vars.json ReserveBooking \
		--parameter-overrides SharedLibsLayer=${SHARED_LIBS_LAYER} \
		--profile ${PROFILE}

deploy: ##=> Deploy booking service using SAM
# [24-07-2020] Changed from `sam deploy` to `aws cloudformation deploy`
# known issue: https://github.com/awslabs/aws-sam-cli/issues/1698
	$(info [*] Packaging and deploying Booking service...)
	sam package \
		--s3-bucket $${DEPLOYMENT_BUCKET_NAME} \
		--output-template-file packaged.yaml && \
	aws cloudformation deploy \
		--template-file packaged.yaml \
		--stack-name $${STACK_NAME}-booking-$${AWS_BRANCH} \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			BookingTable=/$${AWS_BRANCH}/service/amplify/storage/table/booking \
			FlightTable=/$${AWS_BRANCH}/service/amplify/storage/table/flight \
			CollectPaymentFunction=/$${AWS_BRANCH}/service/payment/function/collect \
			RefundPaymentFunction=/$${AWS_BRANCH}/service/payment/function/refund \
			AppsyncApiId=/$${AWS_BRANCH}/service/amplify/api/id \
			Stage=$${AWS_BRANCH} \
			SharedLibsLayer=/$${AWS_BRANCH}/shared/lambda/layers/projectArn

delete: ##=> Delete booking service
	aws cloudformation delete-stack --stack-name $${STACK_NAME}-booking-$${AWS_BRANCH}
