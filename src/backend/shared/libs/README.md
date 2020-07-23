
Lambda Layers for shared dependencies used by the majority of services.

## Implementation

Layers are built using [SAM CLI](https://github.com/awslabs/aws-sam-cli/). It detects our explicit dependencies within `src/requirements.txt`, and prepares the [folder structure](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path) expected by Lambda.

### Parameter store

`{env}` being a git branch from where deployment originates (e.g. twitch):

Parameter | Description
------------------------------------------------- | ---------------------------------------------------------------------------------
/{env}/shared/lambda/layers/projectArn | Lambda Layer ARN for shared libs at project level

## Decisions log
