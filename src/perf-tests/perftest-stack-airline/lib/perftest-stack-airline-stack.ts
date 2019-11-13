import cdk = require('@aws-cdk/core');

const COGNITO_USER_POOL_ARN = process.env.COGNITO_USER_POOL_ARN;

export class PerftestStackAirlineStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    console.log(`COGNITO_USER_POOL_ARN - ${COGNITO_USER_POOL_ARN}`);

  }
}
