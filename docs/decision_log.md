## Decision log

This file is meant to capture project level decisions that were made in this project and why. In many cases, there are no obvious right answers and we have to make a decision with multiple options.

## 2020-07-22

### Drop Log Processing Stack

#### What

[Log processing stack](https://github.com/aws-samples/aws-serverless-airline-booking/blob/9838966872ee68b2b289200300a506989ef7e442/src/backend/log-processing/template.yaml) helped us:

* Auto-expire all Lambda function CloudWatch Log (CWL) Groups
* Subscribe all Lambda function CWL to a Kinesis Stream
* Create CloudWatch Metrics asynchronously via canonical log lines (akin StatsD) 

#### Why

CloudWatch now allows metric creation asynchronously via [Metric Embedded Format (EMF)](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format_Specification.html) thus making this irrelevant and less costly.

[As we have recently open sourced Lambda Powertools](https://aws.amazon.com/blogs/opensource/simplifying-serverless-best-practices-with-lambda-powertools/) originally created in this project as a shared lib, we have now replaced the log-processing stack with Powertools Metrics utility.

**This reduces deployment time by 2m per build, and our metrics cost by approximately 90 USD per month.**

## 2020-07-24

### Introduce Lambda Layers for shared deps

#### What 

Shared dependencies that are used by more than one service within the project are now bundled as a Lambda Layer - This includes `Lambda Powertools`, `requests`, `boto3`, and a custom `process_booking` middleware.

#### Why

We fully migrated from the [original powertools](https://github.com/aws-samples/aws-serverless-airline-booking/commits/develop/src/backend/shared/lambda_python_powertools) to the [now public OSS version](https://github.com/awslabs/aws-lambda-powertools-python). 

As part of this process, we ported custom logic for processing booking information as part of our ProcessBooking State Machine into a custom Powertools middleware.

**This reduces nearly 4 minutes from our total deployment time improving developer productivity, and reducing a shy four cents per build**
