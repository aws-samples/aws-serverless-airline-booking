#!/bin/sh

DOCKER_LOGIN=$(aws ecr get-login --no-include-email --region eu-west-1)

${DOCKER_LOGIN}

cd gatling-scripts
docker build -t gatling:latest .   
docker tag gatling:latest 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191112143648-gatling:latest
docker push 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191112143648-gatling:latest

cd .. 
cd mock-scripts
docker build -t awsserverlessairline-twitchbase-20191112143648-mockdata-container:latest . 
docker tag awsserverlessairline-twitchbase-20191112143648-mockdata-container:latest 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191112143648-mockdata:latest
docker push 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191112143648-mockdata:latest

## setup users

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191112143648-cluster --task-definition awsserverlessairline-twitchbase-20191112143648-mockdata-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-060e1fa5ff8d9e700,subnet-0a12db84f9f146ca8],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191112143648-mockdata-container,command=./setup-users.py}]"

# # generate token

# aws ecs run-task --cluster awsserverlessairline-twitchbase-20191112143648-cluster --task-definition awsserverlessairline-twitchbase-20191112143648-mockdata-task-def --launch-type "FARGATE" \
# --network-configuration "awsvpcConfiguration={subnets=[subnet-000c7ba4c7ce54f00,subnet-0f5faf32a3cb7eee5],assignPublicIp=ENABLED}" \
# --overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191112143648-mockdata-container,command=./generate-token.py}]"

# load flights

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191112143648-cluster --task-definition awsserverlessairline-twitchbase-20191112143648-mockdata-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-060e1fa5ff8d9e700,subnet-0a12db84f9f146ca8],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191112143648-mockdata-container,command=./load-flight-data.py}]"

## start airline test

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191112143648-cluster --task-definition awsserverlessairline-twitchbase-20191112143648-gatling-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-060e1fa5ff8d9e700,subnet-0a12db84f9f146ca8],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191112143648-gatling-container,command=-s Airline -nr -rf /opt/gatling/results/airline}]" --count 1

## consolidate report

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191112143648-cluster --task-definition awsserverlessairline-twitchbase-20191112143648-gatling-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-060e1fa5ff8d9e700,subnet-0a12db84f9f146ca8],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191112143648-gatling-container,command=-ro Airline}]"

## cleanup
aws ecs run-task --cluster awsserverlessairline-twitchbase-20191112143648-cluster --task-definition awsserverlessairline-twitchbase-20191112143648-mockdata-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-060e1fa5ff8d9e700,subnet-0a12db84f9f146ca8],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191112143648-mockdata-container,command=./cleanup.py}]"
