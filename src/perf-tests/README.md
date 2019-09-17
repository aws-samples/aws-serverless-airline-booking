Things to do
- [ ] Have all the parameters as Environment variables
- [ ] Add Lambda to auto-approve users
- [ ] Enable admin srp-auth


docker run -it gatling:local -s setupUsers

```
    aws ecr get-login --no-include-email --region <region> --profile <profile>
    docker build -t gatling:latest .
    docker tag gatling:latest <ECR_URI>
    docker push <ECR_URI>
```

aws ecs run-task --cluster load-test-cluster --overrides '{"containerOverrides": [{"name": "setup-users","command": ["--simulation","setupusers"]}]}' --task-definition load-test:1 --region eu-west-2 ----network-configuration awsvpcConfiguration={subnets=[string,string]}

