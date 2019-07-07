import cdk = require("@aws-cdk/core");
import lambda = require("@aws-cdk/aws-lambda");
import sns = require("@aws-cdk/aws-sns");
import ssm = require("@aws-cdk/aws-ssm");

import importedTable = require("./imported-dynamo");

import booking = require("./booking");

export class AirlineBackendStack extends cdk.Stack {
  protected BookingTable: importedTable.ImportedDynamoTable;
  protected FlightTable: importedTable.ImportedDynamoTable;

  protected AwsBranch: string;

  /**
   * Create a Step for a StepFunction definition that references a Lambda
   * Function from SSM.
   *
   * @param environmentVariable the name of the environment variable to pull in
   * @param name the name of the function for the resource tree
   */
  createFunctionFromSSMParameter(
    environmentVariable: string,
    name: string
  ): lambda.IFunction {
    // Get the environment variable value (even if null)
    const ssmValue = process.env[environmentVariable];

    // If null, then we can't really continue
    if (ssmValue == null) {
      throw new Error(environmentVariable + " not defined");
    }

    // Create the StringParameter that'll be used to resolve the function arn
    const arn = ssm.StringParameter.fromStringParameterAttributes(
      this,
      name + "Arn",
      {
        parameterName: ssmValue
      }
    );

    // Import the Lambda Function
    return lambda.Function.fromFunctionArn(this, name, arn.stringValue);
  }

  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    if (process.env.AWS_BRANCH == null) {
      throw new Error("AWS_BRANCH not defined");
    }

    this.AwsBranch = process.env.AWS_BRANCH;

    if (process.env.BOOKING_TABLE == null) {
      throw new Error("BOOKING_TABLE not defined");
    }

    if (process.env.FLIGHT_TABLE == null) {
      throw new Error("FLIGHT_TABLE not define");
    }

    const bookingTopic = new sns.Topic(this, "BookingNotification");

    this.BookingTable = new importedTable.ImportedDynamoTable(
      process.env.BOOKING_TABLE
    );
    this.FlightTable = new importedTable.ImportedDynamoTable(
      process.env.FLIGHT_TABLE
    );

    const collectPaymentFunction = this.createFunctionFromSSMParameter(
      "COLLECT_PAYMENT_FUNCTION",
      "CollectPayment"
    );
    const refundPaymentFunction = this.createFunctionFromSSMParameter(
      "REFUND_PAYMENT_FUNCTION",
      "RefundPayment"
    );

    new booking.Booking(this, "Booking", {
      BookingTable: this.BookingTable,
      FlightTable: this.FlightTable,
      CollectPaymentFunction: collectPaymentFunction,
      RefundPaymentFunction: refundPaymentFunction
    });
  }
}
