import { PolicyStatement } from "@aws-cdk/aws-iam";

/**
 * Generate an IAM Policy for CRUD against a given table - just here
 * to workaround this current gap in the official Dynamo High-level construct.
 */
export class DynamoDBCrudPolicy {
  public static forTable(tableArn: string): PolicyStatement {
    return new PolicyStatement({
      actions: [
        "dynamodb:GetItem",
        "dynamodb:DeleteItem",
        "dynamodb:PutItem",
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:UpdateItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:DescribeTable"
      ],
      resources: [tableArn]
    });
  }

  private constructor() {}
}
