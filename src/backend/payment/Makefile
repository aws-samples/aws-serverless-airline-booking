PROFILE := "twitch"
SHARED_LIBS_LAYER ?= "arn:aws:lambda:eu-west-1:231436140809:layer:ProjectSharedLibs:2"

target:
	@$(MAKE) pr

dev:
	pipenv install

format:
	pipenv run isort -rc .
	pipenv run black src
	pipenv run black tests

lint: format
	pipenv run flake8

test:
	pipenv run pytest

test-html:
	pipenv run pytest --cov-report html

pr: lint test 

invoke-collect-payment:
	sam local invoke \
		--event src/collect-payment/event.json \
		--env-vars local-env-vars.json CollectPayment \
		--parameter-overrides SharedLibsLayer=${SHARED_LIBS_LAYER} \
		--profile ${PROFILE}

invoke-refund-payment:
	sam local invoke \
		--event src/refund-payment/event.json \
		--env-vars local-env-vars.json RefundPayment \
		--parameter-overrides SharedLibsLayer=${SHARED_LIBS_LAYER} \
		--profile ${PROFILE}
