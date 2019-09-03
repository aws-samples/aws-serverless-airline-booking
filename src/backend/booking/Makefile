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
	sam local invoke --event src/cancel-booking/event.json --env-vars local-env-vars.json CancelBooking --profile ${PROFILE}

build-confirm-booking:
	sam build ConfirmBooking

invoke-confirm-booking: build-confirm-booking
	sam local invoke --event src/confirm-booking/event.json --env-vars local-env-vars.json ConfirmBooking --profile ${PROFILE}

build-notify-booking:
	sam build NotifyBooking

invoke-notify-booking: build-notify-booking
	sam local invoke --event src/notify-booking/event.json --env-vars local-env-vars.json NotifyBooking --profile ${PROFILE}

build-reserve-booking:
	sam build ReserveBooking

invoke-reserve-booking: build-reserve-booking
	sam local invoke --event src/reserve-booking/event.json --env-vars local-env-vars.json ReserveBooking --profile ${PROFILE}
