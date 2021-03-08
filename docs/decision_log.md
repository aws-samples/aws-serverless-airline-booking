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

## 2021-03-08

### Upgrade Quasar 0.x to 1.x, Amplify 2.x to 3.x, and UI refresh
#### What 

Quasar (UI framework) had a major release and deprecated the 0.17 version, and soon after Amplify had a major release cut as well as completely refactored UI components such as Auth.

While Quasar had a [great upgrade guide](https://quasar.dev/start/upgrade-guide#Upgrading-from-0.x-to-v1) there were components and style changes that would no longer fit in the project, thus requiring at least a month or so to get familiar with the new docs, structure, and recreate what we had.

Given the size of changes, it is best to to treat as a new version as it cannot be easily synced into one's fork.
#### Why

Both Quasar and Amplify JS are fundamental to this project, and using deprecated versions meant we had to spend more time working around CVEs encountered in transitive dependencies along with other fixes. 

This upgrade gives us two major benefits: **1/** Eliminates patching CVEs and transitive dependencies, and **2/** Pays technical debt in time to do another major upgrade (Vue 3, Quasar v2), where it'll further simplify the Frontend.

Due to the amount of breaking changes in Quasar, and Amplify's move to [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components) , we had to recreate the UI from scratch as tools also changed, and with this we had a chance to make the following minor improvements:

* Search flight orientation can now swap departure/arrival
* Flight results now have a toolbar to quickly change flight schedule, including a new set of Filter we will implement later on
* Profile no longer has preferences as they were unused
* Flight cards and bookings are cleaner and more modern
* Up to 30% perf improvement due to Quasar upgrade
* [UI prototype is now available](https://www.figma.com/file/Xtdkg865tOPTU3pdCvwMcn/Airline-App?node-id=0%3A1) for anyone to recreate in anticipation of a hardcore workshop to be published later on
* Flight autocomplete is now a separate mixin making it easier to reuse (more to come for a new Booking toolbar)
* Quasar supports dotenv so no more need for `VUE_APP_<VAR>` environment variables
