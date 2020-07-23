PROFILE := "twitch"
SHARED_LIBS_LAYER ?= "arn:aws:lambda:eu-west-1:231436140809:layer:SharedLibsLayer:12"

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
