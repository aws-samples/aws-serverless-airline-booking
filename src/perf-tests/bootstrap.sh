#!/usr/bin/env bash

YELLOW='\033[1;33m'
NC='\033[0m' 
AWS_REGION="eu-west-1"
FOLDERPATH="./"
KEY_COGNITO_CLIENT_ID="/twitchbase/service/amplify/auth/userpool/clientId"
KEY_STRIPE_PUBLIC_KEY="/twitchbase/service/payment/stripe/publicKey"
KEY_USER_POOL_ID="/twitchbase/service/amplify/auth/userpool/id"
KEY_APPSYNC_API_KEY="/twitchbase/service/amplify/api/id"
KEY_S3_BUCKET="/twitchbase/service/s3/loadtest/bucket"
KEY_COGNITO_URL="/twitchbase/service/auth/userpool/url"
KEY_APPSYNC_URL="/twitchbase/service/amplify/api/url"
KEY_API_URL="/twitchbase/service/payment/api/charge/url"
KEY_USER_COUNT="/twitchbase/service/loadtest/usercount"
KEY_DURATION="/twitchbase/service/loadtest/duration"
KEY_TOKEN_CSV="/twitchbase/service/loadtest/csv/token"
KEY_USER_CSV="/twitchbase/service/loadtest/csv/user"

echo -e "${YELLOW}***** Building the docker images  ***** ${NC}"
docker-compose build

echo -e "${YELLOW}***** Fetching environment variables ***** ${NC}"

APPSYNC_API_KEY=`aws ssm get-parameters --names /twitchbase/service/amplify/api/id --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
COGNITO_URL=`aws ssm get-parameters --names /twitchbase/service/auth/userpool/url --region ${AWS_REGION} --query "Parameters[*].Value" --output text`

echo "AWS_REGION=${AWS_REGION}" > setup.env
echo "FOLDERPATH=${FOLDERPATH}" >> setup.env
echo "APPSYNC_API_KEY=${APPSYNC_API_KEY}" >> setup.env
echo "COGNITO_URL=${COGNITO_URL}" >> setup.env

ssmParameters=`aws ssm get-parameters \
                --names ${KEY_COGNITO_CLIENT_ID} \
                        ${KEY_STRIPE_PUBLIC_KEY} \
                        ${KEY_USER_POOL_ID} \
                        ${KEY_USER_COUNT} \
                        ${KEY_DURATION} \
                        ${KEY_API_URL} \
                        ${KEY_APPSYNC_URL} \
                        ${KEY_COGNITO_URL} \
                        ${KEY_S3_BUCKET} \
                        ${KEY_USER_CSV} \
                --region ${AWS_REGION} --query "Parameters[*]"`

for row in $(echo "${ssmParameters}" | jq -r '.[] | @base64'); do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }

    if [ "$(_jq '.Name')" == "${KEY_COGNITO_CLIENT_ID}" ]; then
        echo "COGNITO_CLIENT_ID="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_STRIPE_PUBLIC_KEY}" ]; then
        echo "STRIPE_PUBLIC_KEY="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_USER_POOL_ID}" ]; then
        echo "USER_POOL_ID="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_USER_COUNT}" ]; then
        echo "USER_COUNT="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_DURATION}" ]; then
        echo "DURATION="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_API_URL}" ]; then
        echo "API_URL="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_APPSYNC_URL}" ]; then
        echo "APPSYNC_URL="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_COGNITO_URL}" ]; then
        echo "COGNITO_URL="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_S3_BUCKET}" ]; then
        echo "S3_BUCKET="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_USER_CSV}" ]; then
        echo "USER_CSV="$(_jq '.Value')"" >> setup.env
    elif [ "$(_jq '.Name')" == "${KEY_TOKEN_CSV}" ]; then
        echo "TOKEN_CSV="$(_jq '.Value')"" >> setup.env
    fi
done



# echo "AWS_REGION=${AWS_REGION}" > setup.env
# echo "TOKEN_CSV=${TOKEN_CSV}" >> setup.env
# echo "USER_CSV=${USER_CSV}" >> setup.env
# echo "FOLDERPATH=${FOLDERPATH}" >> setup.env
# echo "COGNITO_CLIENT_ID=${COGNITO_CLIENT_ID}" >> setup.env
# echo "USER_POOL_ID=${USER_POOL_ID}" >> setup.env
# echo "APPSYNC_API_KEY=${APPSYNC_API_KEY}" >> setup.env
# echo "S3_BUCKET=${S3_BUCKET}" >> setup.env
# echo "COGNITO_URL=${COGNITO_URL}" >> setup.env
# echo "APPSYNC_URL=${APPSYNC_URL}" >> setup.env
# echo "API_URL=${API_URL}" >> setup.env
# echo "STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}" >> setup.env
# echo "DURATION=${DURATION}" >> setup.env
# echo "USER_COUNT=${USER_COUNT}" >> setup.env


