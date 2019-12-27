PROFILE := "twitch"

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

build-collect-payment:
	sam build CollectPayment

invoke-collect-payment: build-collect-payment
	sam local invoke --event src/collect-payment/event.json --env-vars local-env-vars.json CollectPayment --profile ${PROFILE}

build-refund-payment:
	sam build RefundPayment

invoke-refund-payment: build-refund-payment
	sam local invoke --event src/refund-payment/event.json --env-vars local-env-vars.json RefundPayment --profile ${PROFILE}
