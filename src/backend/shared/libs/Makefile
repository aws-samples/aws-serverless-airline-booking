deploy: ##=> Deploy shared Lambda Layers using SAM
	$(info [*] Packaging and deploying shared Lambda libs layers...)
	sam build && \
	sam package \
		--s3-bucket $${DEPLOYMENT_BUCKET_NAME} \
		--output-template-file packaged.yaml && \
	sam deploy \
		--template-file packaged.yaml \
		--stack-name $${STACK_NAME}-shared-layers-$${AWS_BRANCH} \
		--parameter-overrides Stage=$${AWS_BRANCH} \
		--capabilities CAPABILITY_IAM

delete: ##=> Delete shared Lambda layers stack
	aws cloudformation delete-stack --stack-name $${STACK_NAME}-shared-layers-$${AWS_BRANCH}
