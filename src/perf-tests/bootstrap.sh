#!/usr/bin/env bash

YELLOW='\033[1;33m'
NC='\033[0m' 
AWS_REGION="eu-west-1"

echo -e "${YELLOW}***** Building the docker images  ***** ${NC}"
# docker-compose build

echo -e "${YELLOW}***** Fetching environment variables ***** ${NC}"

COGNITO_CLIENT_ID=`aws ssm get-parameters --names /twitchbase/service/amplify/auth/userpool/clientId --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
STRIPE_PUBLIC_KEY=`aws ssm get-parameters --names /twitchbase/service/payment/stripe/publicKey --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
USER_POOL_ID=`aws ssm get-parameters --names /twitchbase/service/amplify/auth/userpool/id --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
APPSYNC_API_KEY=`aws ssm get-parameters --names /twitchbase/service/amplify/api/id --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
S3_BUCKET=`aws ssm get-parameters --names /twitchbase/service/s3/loadtest/bucket --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
COGNITO_URL=`aws ssm get-parameters --names /twitchbase/service/auth/userpool/url --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
GRAPHQL_URL=`aws ssm get-parameters --names /twitchbase/service/amplify/api/url --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
API_URL=`aws ssm get-parameters --names /twitchbase/service/payment/api/charge/url --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
USER_COUNT=`aws ssm get-parameters --names /twitchbase/service/service/loadtest/usercount --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
DURATION=`aws ssm get-parameters --names /twitchbase/service/service/loadtest/duration --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
FOLDERPATH=./
TOKEN_CSV='user-with-token.csv'
USER_CSV='user.csv'

echo "AWS_REGION=${AWS_REGION}" > setup.env
echo "TOKEN_CSV=${TOKEN_CSV}" >> setup.env
echo "USER_CSV=${USER_CSV}" >> setup.env
echo "FOLDERPATH=${FOLDERPATH}" >> setup.env
echo "COGNITO_CLIENT_ID=${COGNITO_CLIENT_ID}" >> setup.env
echo "USER_POOL_ID=${USER_POOL_ID}" >> setup.env
echo "APPSYNC_API_KEY=${APPSYNC_API_KEY}" >> setup.env
echo "S3_BUCKET=${S3_BUCKET}" >> setup.env
echo "COGNITO_URL=${COGNITO_URL}" >> setup.env
echo "GRAPHQL_URL=${GRAPHQL_URL}" >> setup.env
echo "API_URL=${API_URL}" >> setup.env
echo "STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}" >> setup.env
echo "DURING_TIME=${DURING_TIME}" >> setup.env
echo "USER_COUNT=${USER_COUNT}" >> setup.env


