import cdk = require("@aws-cdk/core");
import sfn = require("@aws-cdk/aws-stepfunctions");

/**
 * TODO(leepac): We don't cover all the options here, just the ones we
 * need to build our Step Functions for the airline booking system
 */

/**
 * DynamoValue provides a quick way of producing the S/N and the value
 * from either a token or a resolved value. There's a lot more types than
 * this - but we only need S and N.
 */
export class DynamoValue {
  public static fromString(s: string) {
    return new DynamoValue({ S: s });
  }

  public static fromNumber(n: number) {
    if (!cdk.Token.isUnresolved(n)) {
      return new DynamoValue({ N: `${n}` });
    } else {
      return new DynamoValue({ N: n });
    }
  }

  protected constructor(public readonly value: any) {}
}

/**
 * Properties for the UpdateItem task.
 */
export interface UpdateItemProps {
  /**
   * tableName is the table we'll be updating or a StepFunction reference
   */
  readonly tableName: string;

  /**
   * The field used as the key
   */
  readonly key: string;

  /**
   * updateExpressions is the expression run to update the item
   */
  readonly updateExpression: string;

  /**
   * conditionExpression provides for an optional condition expression used
   * to look up the item to update.
   */
  readonly conditionExpression?: string;

  /**
   * Any variable replacements for the expressions above.
   */
  readonly expressionAttributeValues: { [key: string]: DynamoValue };
}

/**
 * Ref: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html
 */
export class UpdateItem implements sfn.IStepFunctionsTask {
  private readonly tableName: string;
  private readonly updateExpression: string;
  private readonly conditionExpression?: string;
  private readonly key: string;
  private readonly expressionAttributeValues: { [key: string]: DynamoValue };

  constructor(props: UpdateItemProps) {
    this.tableName = props.tableName;
    this.updateExpression = props.updateExpression;
    this.conditionExpression = props.conditionExpression;
    this.expressionAttributeValues = props.expressionAttributeValues;
    this.key = props.key;
  }

  public bind(task: sfn.Task): sfn.StepFunctionsTaskConfig {
    return {
      resourceArn: "arn:aws:states:::dynamodb:updateItem",
      parameters: {
        "TableName.$": this.tableName,
        ConditionExpression: this.conditionExpression,
        UpdateExpression: this.updateExpression,
        Key: {
          id: {
            "S.$": this.key
          }
        },
        ExpressionAttributeValues: this.expressionAttributeValues
      }
    };
  }
}
