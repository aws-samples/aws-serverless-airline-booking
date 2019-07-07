import cdk = require("@aws-cdk/core");

export class ImportedDynamoTable {
  public get Arn(): string {
    return [
      "arn",
      cdk.Aws.PARTITION,
      "dynamodb",
      cdk.Aws.REGION,
      cdk.Aws.ACCOUNT_ID,
      "table/" + this.Name
    ].join(":");
  }

  constructor(public readonly Name: string) {}
}
