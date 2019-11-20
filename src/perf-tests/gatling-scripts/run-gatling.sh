#!/usr/bin/env bash

aws s3api get-object --bucket ${S3_BUCKET} --key ${TOKEN_CSV} /opt/gatling/user-files/resources/${TOKEN_CSV} --region ${AWS_REGION}
aws s3 sync s3://${S3_BUCKET}/results /opt/gatling/results

# Run gatling
JAVA_OPTS="-Dsun.net.inetaddr.ttl=10" /opt/gatling/bin/gatling.sh -bf /opt/gatling/user-files/bin $@

# Sync report and logs to S3
aws s3 sync /opt/gatling/results/ s3://${S3_BUCKET}/results

