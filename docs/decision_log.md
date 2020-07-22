## Decision log

This file is meant to capture all the architectural decisions that were made in this project and why. In many cases, there are no obvious right answers and we have to make a decision with multiple options.

## 2020-07-22

### Drop Log Processing Stack

Log processing stack helped us create CloudWatch Metrics asynchronously by using a combination of canonical log lines (ala StatsD), and a custom log processing Lambda listening to a Kinesis stream that calls CloudWatch PutMetricData in batches - CloudWatch now allows metric creation asynchronously via [Metric Embedded Format (EMF)](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format_Specification.html), making this irrelevant.

[As we have recently open sourced our original Powertools implementation](https://aws.amazon.com/blogs/opensource/simplifying-serverless-best-practices-with-lambda-powertools/) created in this project, we have now replaced the log-processing stack with Powertools Metrics.
