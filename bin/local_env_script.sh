#!/bin/bash

set -o errexit  # abort on nonzero exitstatus
set -o pipefail # don't hide errors within pipes
# set -x           # Debugging

NOCOLOR="\033[0m"
BOLD='\033[1;37m'
ENV_VARS=(AWS_DEFAULT_REGION AWS_BRANCH FLIGHT_TABLE_NAME BOOKING_TABLE_NAME STACK_NAME DEPLOYMENT_BUCKET_NAME GRAPHQL_API_ID VUE_APP_StripePublicKey VUE_APP_PaymentChargeUrl)

function fetch_env_vars() {
    echo -e "[*] Fetching environment variables from Parameter Store in ${BOLD}default region: ${AWS_DEFAULT_REGION}${NOCOLOR}"
    FLIGHT_TABLE_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/storage/table/flight --query 'Parameter.Value' --output text &)
    BOOKING_TABLE_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/storage/table/booking --query 'Parameter.Value' --output text &)
    STACK_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/deployment/stackName --query 'Parameter.Value' --output text &)
    DEPLOYMENT_BUCKET_NAME=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/deployment/deploymentBucket --query 'Parameter.Value' --output text &)
    GRAPHQL_API_ID=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/amplify/api/id --query 'Parameter.Value' --output text &)
    VUE_APP_StripePublicKey=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/payment/stripe/publicKey --query 'Parameter.Value' --output text &)
    VUE_APP_PaymentChargeUrl=$(aws ssm get-parameter --name /${AWS_BRANCH}/service/payment/api/charge/url --query 'Parameter.Value' --output text &)

    wait
}

function print_vars() {
    for env in ${ENV_VARS[@]}; do
        echo -e \\t "export $env=${!env}"
    done

    echo -e "\\n"
}

function prompt_aws_cli_profile() {
    echo -e "[*] Listing current AWS CLI profiles" \\n
    grep -o '\[[^]]*\]' ~/.aws/credentials && echo -e "\\n"
    echo -en "[?] Which ${BOLD}AWS CLI profile${NOCOLOR} would you like to use:  "
    read AWS_PROFILE
}

function prompt_amplify_env() {
    echo -e "[*] Listing Amplify environments available"
    amplify env list
    echo -en "[?] Which ${BOLD}Amplify environment${NOCOLOR} would you like to use:  "
    read AWS_BRANCH
}

function prompt_aws_region() {
    echo -e "[*] Listing current AWS regions" \\n
    aws ec2 describe-regions --query 'Regions[].RegionName' --output table
    echo -en "[?] Which ${BOLD}AWS region${NOCOLOR} would you like to use:  "
    read AWS_DEFAULT_REGION
}

function prompt_options() {
    echo -e "${BOLD}[+] Using AWS Profile detected: [${AWS_PROFILE}]${NOCOLOR}"
    echo -e "${BOLD}[+] Using AWS Region detected: [${AWS_DEFAULT_REGION}]${NOCOLOR}"
    test -z $AWS_PROFILE && prompt_aws_cli_profile
    test -z $AWS_DEFAULT_REGION && prompt_aws_region
    prompt_amplify_env
}

function main() {
    echo ${AWS_PROFILE}
    prompt_options
    fetch_env_vars
    test -z ${AWS_DEFAULT_REGION} || test -z ${AWS_PROFILE} && echo -e "[*] Next time, you can also use AWS_DEFAULT_REGION and AWS_PROFILE, if necessary" \\n
    echo -e "[+] ${BOLD}Copy and paste the env vars below${NOCOLOR}" \\n
    print_vars
}

main
