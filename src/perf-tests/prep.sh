#!/bin/sh

DOCKER_LOGIN=$(aws ecr get-login --no-include-email --region eu-west-1)

${DOCKER_LOGIN}

cd gatling-scripts
docker build -t gatling:latest .   
docker tag gatling:latest 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191121221048-gatling:latest
docker push 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191121221048-gatling:latest

cd .. 
cd mock-scripts
docker build -t mockdata:latest . 
docker tag mockdata:latest 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191121221048-mockdata:latest
docker push 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20191121221048-mockdata:latest

## setup users

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191121221048-cluster --task-definition awsserverlessairline-twitchbase-20191121221048-mockdata-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-0bcaa099575b61122,subnet-0de420966d1049949],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191121221048-mockdata-container,command=./setup-users.py}]"

# # generate token

# aws ecs run-task --cluster awsserverlessairline-twitchbase-20191121221048-cluster --task-definition awsserverlessairline-twitchbase-20191121221048-gatling --launch-type "FARGATE" \
# --network-configuration "awsvpcConfiguration={subnets=[subnet-000c7ba4c7ce54f00,subnet-0f5faf32a3cb7eee5],assignPublicIp=ENABLED}" \
# --overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191121221048-gatling-container,command=./generate-token.py}]"

# load flights

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191121221048-cluster --task-definition awsserverlessairline-twitchbase-20191121221048-mockdata-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-0bcaa099575b61122,subnet-0de420966d1049949],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191121221048-mockdata-container,command=./load-flight-data.py}]"

## start airline test

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191121221048-cluster --task-definition awsserverlessairline-twitchbase-20191121221048-gatling --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-0bcaa099575b61122,subnet-0de420966d1049949],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191121221048-gatling-container,command=-s Airline -nr -rf /opt/gatling/results/airline}]" --count 1

## consolidate report

aws ecs run-task --cluster awsserverlessairline-twitchbase-20191121221048-cluster --task-definition awsserverlessairline-twitchbase-20191121221048-gatling --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-0bcaa099575b61122,subnet-0de420966d1049949],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191121221048-gatling-container,command=-ro airline}]"

## cleanup
aws ecs run-task --cluster awsserverlessairline-twitchbase-20191121221048-cluster --task-definition awsserverlessairline-twitchbase-20191121221048-mockdata-task-def --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-0bcaa099575b61122,subnet-0de420966d1049949],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20191121221048-mockdata-container,command=./cleanup.py}]"
