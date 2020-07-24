
Lambda Layers for shared dependencies used by the majority of services.

## Implementation

Layers are built using [SAM CLI](https://github.com/awslabs/aws-sam-cli/). It detects our explicit dependencies within `src/requirements.txt`, includes any additional python code within `src`, and prepares the [folder structure](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path) expected by Lambda.

### Parameter store

`{env}` being a git branch from where deployment originates (e.g. twitch):

Parameter | Description
------------------------------------------------- | ---------------------------------------------------------------------------------
/{env}/shared/lambda/layers/projectArn | Lambda Layer ARN for shared libs at project level

## Decisions log

Decision | Description | Timeframe
------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------
Include `process_booking` middleware | Booking and Payment functions are invoked via Process Booking State Machine. All functions utilize a key information from state machine input to add tracer annotation as well as inject that info into their loggers. This addition bundles all this custom logic as a custom middleware. | July 24th 2020
