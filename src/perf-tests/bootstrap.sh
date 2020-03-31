# #!/usr/bin/env bash

YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

main() {
    AWS_REGION=${1:-"eu-west-1"}
    AWS_BRANCH=${2:-"twitchbase"}
    FOLDERPATH="./"
    KEY_COGNITO_CLIENT_ID="/${AWS_BRANCH}/service/amplify/auth/userpool/clientId"
    KEY_STRIPE_PUBLIC_KEY="/${AWS_BRANCH}/service/payment/stripe/publicKey"
    KEY_USER_POOL_ID="/${AWS_BRANCH}/service/amplify/auth/userpool/id"
    KEY_APPSYNC_API_KEY="/${AWS_BRANCH}/service/amplify/api/id"
    KEY_S3_BUCKET="/${AWS_BRANCH}/service/s3/loadtest/bucket"
    KEY_COGNITO_URL="/${AWS_BRANCH}/service/auth/userpool/url"
    KEY_APPSYNC_URL="/${AWS_BRANCH}/service/amplify/api/url"
    KEY_API_URL="/${AWS_BRANCH}/service/payment/api/charge/url"
    KEY_USER_COUNT="/${AWS_BRANCH}/service/loadtest/usercount"
    KEY_DURATION="/${AWS_BRANCH}/service/loadtest/duration"
    KEY_TOKEN_CSV="/${AWS_BRANCH}/service/loadtest/csv/token"
    KEY_USER_CSV="/${AWS_BRANCH}/service/loadtest/csv/user"
    KEY_APPSYNC_API_KEY="/${AWS_BRANCH}/service/amplify/api/id"
    KEY_COGNITO_URL="/${AWS_BRANCH}/service/auth/userpool/url"
    KEY_TOKEN_CSV="/${AWS_BRANCH}/service/loadtest/csv/token"

    echo -e "${YELLOW}***** Fetching environment variables ***** ${NC}"

    APPSYNC_API_KEY=`aws ssm get-parameters --names ${KEY_APPSYNC_API_KEY} --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
    COGNITO_URL=`aws ssm get-parameters --names ${KEY_COGNITO_URL} --region ${AWS_REGION} --query "Parameters[*].Value" --output text`
    TOKEN_CSV=`aws ssm get-parameters --names ${KEY_TOKEN_CSV} --region ${AWS_REGION} --query "Parameters[*].Value" --output text`

    echo "AWS_REGION=${AWS_REGION}" > setup.env
    echo "FOLDERPATH=${FOLDERPATH}" >> setup.env
    echo "APPSYNC_API_KEY=${APPSYNC_API_KEY}" >> setup.env
    echo "COGNITO_URL=${COGNITO_URL}" >> setup.env
    echo "TOKEN_CSV=${TOKEN_CSV}" >> setup.env

    json_key() {        
        echo $1 | base64 --decode | jq -r $2
    }
    
    ssmParameters=$(aws ssm get-parameters \
                        --names "${KEY_COGNITO_CLIENT_ID}" \
                                "${KEY_STRIPE_PUBLIC_KEY}" \
                                "${KEY_USER_POOL_ID}" \
                                "${KEY_USER_COUNT}" \
                                "${KEY_DURATION}" \
                                "${KEY_API_URL}" \
                                "${KEY_APPSYNC_URL}" \
                                "${KEY_COGNITO_URL}" \
                                "${KEY_S3_BUCKET}" \
                                "${KEY_USER_CSV}" \
                        --region "${AWS_REGION}" --query "Parameters[*]")

    parameters=$(echo "${ssmParameters}" | jq -r '.[] | @base64')
 
    for row in ${parameters}; do
        if [ "$(json_key ${row} '.Name')" == "${KEY_COGNITO_CLIENT_ID}" ]; then
            echo "COGNITO_CLIENT_ID=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_STRIPE_PUBLIC_KEY}" ]; then
            echo "STRIPE_PUBLIC_KEY=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_USER_POOL_ID}" ]; then
            echo "USER_POOL_ID=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_USER_COUNT}" ]; then
            echo "USER_COUNT=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_DURATION}" ]; then
            echo "DURATION=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_API_URL}" ]; then
            echo "API_URL=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_APPSYNC_URL}" ]; then
            echo "APPSYNC_URL=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_COGNITO_URL}" ]; then
            echo "COGNITO_URL=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_S3_BUCKET}" ]; then
            echo "S3_BUCKET=$(json_key ${row} '.Value')" >> setup.env
        elif [ "$(json_key ${row} '.Name')" == "${KEY_USER_CSV}" ]; then
            echo "USER_CSV=$(json_key ${row} '.Value')" >> setup.env
        fi
    done

    echo -e "${YELLOW}***** Completed creating setup.env ***** ${NC}"


    echo -e "${YELLOW}***** Building the docker images  ***** ${NC}"
    docker-compose build

    echo -e "${YELLOW}***** Completed Building the docker images  ***** ${NC}"
}

read -rp "Enter AWS region and AWS Branch name => eg: eu-west-1 twitchbase : " inputs
eval "main $inputs"