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

build-cancel-booking:
	sam build CancelBooking

invoke-cancel-booking: build-cancel-booking
	sam build CancelBooking
	sam local invoke --event src/cancel-booking/event.json --env-vars local-env-vars.json CancelBooking --profile ${PROFILE}
