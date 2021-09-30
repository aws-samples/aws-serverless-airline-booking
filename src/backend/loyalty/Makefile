dev:
	pip install -U poetry
	poetry install

deploy: ##=> Deploy loyalty service using SAM and TypeScript build
	$(info [*] Packaging and deploying Loyalty service...)
	sam build --cached --use-container -m requirements.txt && \
	sam deploy \
		--stack-name $${STACK_NAME}-loyalty-$${AWS_BRANCH} \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			BookingSNSTopic=/$${AWS_BRANCH}/service/booking/messaging/bookingTopic \
			Stage=$${AWS_BRANCH} \
			AppsyncApiId=$${GRAPHQL_API_ID} \
			SharedLibsLayer=/$${AWS_BRANCH}/shared/lambda/layers/projectArn \
		--resolve-s3

delete: ##=> Delete booking service
	sam delete --stack-name $${STACK_NAME}-loyalty-$${AWS_BRANCH}

format:
	poetry run isort src/loyalty tests
	poetry run black src/loyalty tests

lint: format
	poetry run flake8 src/loyalty tests

test: unit-test integ-test

unit-test:
	poetry run pytest tests/unit
	poetry run pytest tests/storage

integ-test:
	STAGE=test poetry run pytest tests/integ

coverage-html:
	poetry run pytest -m "not perf" --cov=aws_lambda_powertools --cov-report=html

static-analysis:
	poetry run mypy --pretty src/loyalty

pr: lint static-analysis
