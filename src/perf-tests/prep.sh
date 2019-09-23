#!/bin/sh

DOCKER_LOGIN=$(aws ecr get-login --no-include-email --region eu-west-1)

${DOCKER_LOGIN}

cd gatling-scripts
docker build -t gatling:latest .   
docker tag gatling:latest 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20190919161601-gatling:latest
docker push 963887453151.dkr.ecr.eu-west-1.amazonaws.com/awsserverlessairline-twitchbase-20190919161601-gatling:latest

cd .. 
cd mock-scripts
docker build -t generate-data:latest . 
docker tag generate-data:latest 963887453151.dkr.ecr.eu-west-1.amazonaws.com/generate-data:latest
docker push 963887453151.dkr.ecr.eu-west-1.amazonaws.com/generate-data:latest

## setup users

aws ecs run-task --cluster awsserverlessairline-twitchbase-20190919161601-cluster --task-definition awsserverlessairline-twitchbase-20190919161601-fargate-task-def:1 --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-000c7ba4c7ce54f00,subnet-0f5faf32a3cb7eee5],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20190919161601-container,command=-s SetUpUsers}]"

# generate token

aws ecs run-task --cluster awsserverlessairline-twitchbase-20190919161601-cluster --task-definition generate-data:1 --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-000c7ba4c7ce54f00,subnet-0f5faf32a3cb7eee5],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=generate-data,command=./generate-token.py}]"

# load flights

aws ecs run-task --cluster awsserverlessairline-twitchbase-20190919161601-cluster --task-definition generate-data:1 --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-000c7ba4c7ce54f00,subnet-0f5faf32a3cb7eee5],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=generate-data,command=./load-flight-data.py}]"

# ## start airline test

aws ecs run-task --cluster awsserverlessairline-twitchbase-20190919161601-cluster --task-definition awsserverlessairline-twitchbase-20190919161601-fargate-task-def:1 --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[subnet-000c7ba4c7ce54f00,subnet-0f5faf32a3cb7eee5],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=awsserverlessairline-twitchbase-20190919161601-container,command=-s Airline}]" \
--count 2
