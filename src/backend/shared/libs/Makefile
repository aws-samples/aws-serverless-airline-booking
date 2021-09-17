deploy: ##=> Deploy shared Lambda Layers using SAM
	$(info [*] Packaging and deploying shared Lambda libs layers...)
	sam build --use-container && \
	sam deploy \
		--stack-name $${STACK_NAME}-shared-layers-$${AWS_BRANCH} \
		--parameter-overrides Stage=$${AWS_BRANCH} \
		--capabilities CAPABILITY_IAM \
		--resolve-s3

delete: ##=> Delete shared Lambda layers stack
	aws cloudformation delete-stack --stack-name $${STACK_NAME}-shared-layers-$${AWS_BRANCH}
