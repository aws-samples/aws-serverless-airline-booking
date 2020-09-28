deploy: ##=> Deploying Gatling components for performance testing
	$(info [*] Deploying Gatling components for performance testing ...)
	cd perftest-stack-airline && \
		npm install && \
		npm run build && \
		cdk list && \
		cdk bootstrap && \
		cdk deploy $${PERF_TEST_STACK_NAME} --require-approval never

delete: ##=> Delete performance testing stack
	cdk destroy $${PERF_TEST_STACK_NAME}
