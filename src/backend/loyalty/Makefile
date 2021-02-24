deploy: ##=> Deploy loyalty service using SAM and TypeScript build
	$(info [*] Packaging and deploying Loyalty service...)
	npm install && \
	npm run build && \
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
