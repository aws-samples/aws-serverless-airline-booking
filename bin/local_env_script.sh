#!/bin/bash

set -o errexit  # abort on nonzero exitstatus
set -o pipefail # don't hide errors within pipes
# set -x           # Debugging

NOCOLOR="\033[0m"
BOLD='\033[1;37m'

function fetch_env_vars() {
    echo -e "[*] Fetching environment variables from Parameter Store in ${BOLD} region: ${AWS_DEFAULT_REGION}${NOCOLOR}"
    FLIGHT_TABLE_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/storage/table/flight --query 'Parameter.Value' --output text &)
    BOOKING_TABLE_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/storage/table/booking --query 'Parameter.Value' --output text &)
    STACK_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/deployment/stackName --query 'Parameter.Value' --output text &)
    DEPLOYMENT_BUCKET_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/deployment/deploymentBucket --query 'Parameter.Value' --output text &)
    GRAPHQL_API_ID=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/api/id --query 'Parameter.Value' --output text &)
    VUE_APP_StripePublicKey=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/payment/stripe/publicKey --query 'Parameter.Value' --output text &)
    VUE_APP_PaymentChargeUrl=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/payment/api/charge/url --query 'Parameter.Value' --output text &)
    SHARED_LIBS_LAYER=$(aws ssm get-parameter --name /${AWS_BRANCH}/shared/lambda/layers/projectArn --query 'Parameter.Value' --output text &)
    wait
}

function print_vars() {
    ENV_VARS=(AWS_DEFAULT_REGION AWS_BRANCH FLIGHT_TABLE_NAME BOOKING_TABLE_NAME STACK_NAME DEPLOYMENT_BUCKET_NAME GRAPHQL_API_ID SHARED_LIBS_LAYER VUE_APP_StripePublicKey VUE_APP_PaymentChargeUrl)

    for env in ${ENV_VARS[@]}; do
        echo -e "${BOLD}export $env=${!env}${NOCOLOR}"
    done
}

function prompt_aws_cli_profile() {
    echo -e "[*] Listing current AWS CLI profiles" \\n
    grep -o '\[[^]]*\]' ~/.aws/credentials && echo -e "\\n"
    echo -en "[?] Which ${BOLD}AWS CLI profile${NOCOLOR} would you like to use:  "
    read AWS_DEFAULT_PROFILE
}

function prompt_amplify_env() {
    echo -e "[*] Listing Amplify environments available"
    amplify env list
    echo -en "[?] Which ${BOLD}Amplify environment${NOCOLOR} would you like to use: "
    read AWS_BRANCH
}

function prompt_aws_region() {
    echo -e "[*] Listing current AWS regions" \\n
    aws ec2 describe-regions --query 'Regions[].RegionName' --output table
    echo -en "[?] Which ${BOLD}AWS region${NOCOLOR} would you like to use:  "
    read AWS_DEFAULT_REGION
}

function prompt_options() {
    echo -e "${BOLD}[+] Using AWS Profile detected: [${AWS_DEFAULT_PROFILE}]${NOCOLOR}"
    echo -e "${BOLD}[+] Using AWS Region detected: [${AWS_DEFAULT_REGION}]${NOCOLOR}"
    test -z $AWS_DEFAULT_PROFILE && prompt_aws_cli_profile
    test -z $AWS_DEFAULT_REGION && prompt_aws_region
    prompt_amplify_env
}

function main() {
    echo ${AWS_DEFAULT_PROFILE}
    prompt_options
    fetch_env_vars
    test -z ${AWS_DEFAULT_REGION} || test -z ${AWS_DEFAULT_PROFILE} && echo -e "[*] Next time, you can also use AWS_DEFAULT_REGION and AWS_DEFAULT_PROFILE, if necessary" \\n
    echo -e "[+] ${BOLD}Copy and paste the env vars below${NOCOLOR}" \\n
    print_vars
}

main
