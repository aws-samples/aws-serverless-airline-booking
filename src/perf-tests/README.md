Things to do
- [ ] Have all the parameters as Environment variables
- [ ] New Lambda to auto-approve users
- [ ] Enable admin srp-auth
- [ ] New Lambda listen to ECS stop status to signal step function to go to next task


docker run -it gatling:local -s setupUsers

```
    aws ecr get-login --no-include-email --region <region> --profile <profile>
    docker build -t gatling:latest .
    docker tag gatling:latest <ECR_URI>
    docker push <ECR_URI>
```

