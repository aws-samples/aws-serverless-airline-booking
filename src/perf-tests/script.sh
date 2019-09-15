#! /bin/bash

USAGE="Usage: $0 <AWS PROFILE> <AWS REGION for ECR>"

export AWS_PROFILE=$1
export AWS_DEFAULT_REGION=$2

: ${AWS_PROFILE:?"Missing mandatory aws profile. ${USAGE}"}
: ${AWS_DEFAULT_REGION:?"Missing mandatory aws region. ${USAGE}"}

STAKCNAME=gatling-ecr-repository

aws cloudformation deploy \
    --stack-name ${STAKCNAME} \
    --template-file ./templates/ecr.yaml \
    --parameter-overrides "RepositoryName=gatling-fargate" \
    --no-fail-on-empty-changeset