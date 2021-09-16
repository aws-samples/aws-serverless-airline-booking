deploy: ##=> Deploy loyalty service using SAM and TypeScript build
	$(info [*] Packaging and deploying Loyalty service...)
	sam build --cached --parallel && \
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

delete: ##=> Delete booking service
	aws cloudformation delete-stack --stack-name $${STACK_NAME}-loyalty-$${AWS_BRANCH}

format:
	poetry run isort src/loyalty tests
	poetry run black src/loyalty tests

lint: format
	poetry run flake8 src/loyalty tests

test:
	poetry run pytest tests

coverage-html:
	poetry run pytest -m "not perf" --cov=aws_lambda_powertools --cov-report=html

static-analysis:
	poetry run mypy --pretty src/loyalty

pr: lint static-analysis
