# Tasks:
- [x] Fake usernames for load testing
- [x] Allow load test to run from one's laptop (Docker)
- [ ] Automate parameters as Environment variables
- 


# Steps

1. ecr login
```
aws ecr get-login --no-include-email --region eu-west-1
```

2. docker login
```
docker login -u AWS -p <> https://<_account_id_>.dkr.ecr.eu-west-1.amazonaws.com
```

3. docker builds

```
cd gatling-scripts

docker build -t gatling:latest . 

docker tag gatling:latest <replace_with_YOUR_gatling_ECR_repo_URI>:latest

docker push <replace_with_YOUR_gatling_ECR_repo_URI>:latest
```

repeat this for the mock-scripts

```
cd mock-scripts

docker build -t mockdata:latest . 

docker tag mockdata:latest <replace_with_YOUR_mockdata_ECR_repo_URI>:latest

docker push <replace_with_YOUR_mockdata_ECR_repo_URI>:latest
```

## Run load test locally using docker:

1. docker run -it -v ~/.aws:/root/.aws mockdata:latest setup-users.py 
2. docker run -it -v ~/.aws:/root/.aws mockdata:latest load-flight-data.py
3. docker run -it -v ~/.aws:/root/.aws gatling:latest -s Airline -nr -rf /opt/gatling/results/airline
4. docker run -it -v ~/.aws:/root/.aws gatling:latest -ro airline
5. docker run -it -v ~/.aws:/root/.aws mockdata:latest cleanup.py

## Run load test on AWS:

Execute the `start-load-test` Step function using the following input

```
{
  "commands": [
    "--simulation",
    "setupUsers"
  ]
}
```

This will setup users, load mock flight data, start gatling, consolidate the report to S3 bucket
