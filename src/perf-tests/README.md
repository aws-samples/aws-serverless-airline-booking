Things to do:
- [ ] Have all the parameters as Environment variables
- [ ] Fake usernames for load testing
- [ ] Allow load test to run from one's laptop (Docker)

docker run -it gatling:local -s setupUsers

```
    aws ecr get-login --no-include-email --region <region> --profile <profile>
    docker build -t gatling:latest .
    docker tag gatling:latest <ECR_URI>
    docker push <ECR_URI>
```

1. Get Cognito arn and pass that as input to CDK.