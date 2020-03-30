# Overview

This perf-test stack uses [Gatling](https://gatling.io/), open source tool for load testing. The stack creates AWS Fargate Cluster to run the setup and Gatling scripts.

Under the [Setup | mock-scripts](./setup/mock-scripts) folder, you will find setup scripts that:
- creates test users in Amazon Cognito userpool
- load mock flight data into Flights table
- zips Gatling reports and upload to S3 bucket

The Gatling simulation script uses constantUsersPerSec and rampUsersPerSec to inject users for the given scenarios. By default, it uses `5 users` for a duration of `300 seconds`(`5 minutes`). These can be overridden via Systems Manager Paramater store  

All these steps are co-ordinated using AWS Step functions.

# Steps
After the perf-test stack has been deployed successfully, follow these steps:

1. Run `bootstrap.sh` under the **src/perf-tests** folder. This will build the docker images for `gatling-scripts` and `mock-scripts`. 

    ```
    ./bootstrap.sh
    ```

2. After the environment variables in the DockerFile is updated, we need to push them to Amazon ECR. First login to an Amazon ECR registry
    ```
    aws ecr get-login --no-include-email --region <AWS_REGION>
    ```
    Example:  
    > aws ecr get-login --no-include-email --region eu-west-1

3. Copy paste the docker login command and enter.
    ```
    docker login -u AWS -p <> https://<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com
    ```

4. Tag the docker images and push the latest tagged docker images for `gatling-scripts` and `mock-scripts` to Amazon ECR

    ```
    docker tag gatling:latest <replace_with_YOUR_gatling_ECR_repo_URI>:latest

    docker push <replace_with_YOUR_gatling_ECR_repo_URI>:latest
    ```


    ```
    docker tag mockdata:latest <replace_with_YOUR_mockdata_ECR_repo_URI>:latest

    docker push <replace_with_YOUR_mockdata_ECR_repo_URI>:latest
    ```

## Run load test locally using docker:

1. docker run --env-file=setup.env -it -v ~/.aws:/root/.aws mockdata:latest setup-users.py 
2. docker run --env-file=setup.env -it -v ~/.aws:/root/.aws mockdata:latest load-flight-data.py
3. docker run --env-file=setup.env -it -v ~/.aws:/root/.aws gatling:latest -s Airline -nr -rf /opt/gatling/results/airline
4. docker run --env-file=setup.env -it -v ~/.aws:/root/.aws gatling:latest -ro airline
5. docker run --env-file=setup.env -it -v ~/.aws:/root/.aws mockdata:latest cleanup.py

## Run load test using Step functions:

Start the execution of the `loadtest` Step function using the following input

```
{
  "commands": [
    "./setup-users.py"
  ]
}
```

This will setup users, load mock flight data, start gatling, consolidate the report to **loadtest** S3 bucket

<details>
<summary><strong>Expand you want to run the individual steps manually:</strong></summary><p>

## setup users

aws ecs run-task --cluster CLUSTER_NAME --task-definition TASK_DEFINITION --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[PROVIDE_SUBNET_IDs],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=CONTAINER_NAME,command=./setup-users.py}]"

## load flights

aws ecs run-task --cluster CLUSTER_NAME --task-definition TASK_DEFINITION --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[PROVIDE_SUBNET_IDs],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=CONTAINER_NAME,command=./load-flight-data.py}]"

## start airline test

aws ecs run-task --cluster CLUSTER_NAME --task-definition TASK_DEFINITION --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[PROVIDE_SUBNET_IDs],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=CONTAINER_NAME,command=-s Airline -nr -rf /opt/gatling/results/airline}]" --count 1

## consolidate report

aws ecs run-task --cluster CLUSTER_NAME --task-definition TASK_DEFINITION --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[PROVIDE_SUBNET_IDs],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=CONTAINER_NAME,command=-ro airline}]"

## cleanup
aws ecs run-task --cluster CLUSTER_NAME --task-definition TASK_DEFINITION --launch-type "FARGATE" \
--network-configuration "awsvpcConfiguration={subnets=[PROVIDE_SUBNET_IDs],assignPublicIp=ENABLED}" \
--overrides="containerOverrides=[{name=CONTAINER_NAME,command=./cleanup.py}]"

## Results:

- Download the results.zip folder from the S3 bucket (refer to the perf-test stack output)
- Open the index.html and you should see a report similar to the below

  ![Report](./images/gatling-report.png)

  </p></details>