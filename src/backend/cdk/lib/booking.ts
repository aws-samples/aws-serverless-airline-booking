import cdk = require("@aws-cdk/core");
import lambda = require("@aws-cdk/aws-lambda");
import sfn = require("@aws-cdk/aws-stepfunctions");
import tasks = require("@aws-cdk/aws-stepfunctions-tasks");
import sns = require("@aws-cdk/aws-sns");
import { RetryProps } from "@aws-cdk/aws-stepfunctions";

import path = require("path");

import dynamoTask = require("./dynamo-update-item");
import { DynamoDBCrudPolicy } from "./dynamodbcrud-policy";
import { ImportedDynamoTable } from "./imported-dynamo";

interface BookingProps {
  readonly FlightTable: ImportedDynamoTable;
  readonly BookingTable: ImportedDynamoTable;
  readonly CollectPaymentFunction: lambda.IFunction;
  readonly RefundPaymentFunction: lambda.IFunction;
}

export class Booking extends cdk.Construct {
  private CollectPaymentTask: sfn.Task;
  private RefundPaymentTask: sfn.Task;
  private CancelBookingTask: sfn.Task;
  private ReserveBookingTask: sfn.Task;
  private NotifyBookingFailedTask: sfn.Task;
  private NotifyBookingSucceededTask: sfn.Task;
  private ConfirmBookingTask: sfn.Task;
  private ReserveFlightSeatTask: sfn.Task;
  private ReleaseFlightSeatTask: sfn.Task;
  private readonly BookingConfirmedState: sfn.State;
  private readonly BookingFailedState: sfn.State;

  public readonly NotificationTopic: sns.Topic;

  private get GenericRetry(): RetryProps {
    return {
      maxAttempts: 2,
      backoffRate: 2,
      interval: cdk.Duration.seconds(1)
    };
  }

  private GetReserveFlightSeatTask(): sfn.Task {
    return new sfn.Task(this, "Reserve Flight Seat", {
      task: new dynamoTask.UpdateItem({
        tableName: "$.flightTable",
        key: "$.outboundFlightId",
        updateExpression: "SET seatAllocation = seatAllocation - :dec",
        expressionAttributeValues: {
          ":dec": dynamoTask.DynamoValue.fromNumber(1).value,
          ":noseat": dynamoTask.DynamoValue.fromNumber(0).value
        },
        conditionExpression: "seatAllocation > :noSeat"
      }),
      timeout: cdk.Duration.seconds(5)
    })
      .addRetry({
        errors: [
          "ProvisionedThroughputExceededException",
          "RequestLimitExceeded",
          "ServiceUnavailable",
          "ThrottlingException"
        ],
        interval: cdk.Duration.seconds(1),
        backoffRate: 2,
        maxAttempts: 2
      })
      .addRetry({
        errors: ["ConditionalCheckFailedException"],
        interval: cdk.Duration.seconds(0),
        maxAttempts: 0
      });
  }

  private GetReleaseFlightSeatTask(): sfn.Task {
    return new sfn.Task(this, "Release Flight Seat", {
      task: new dynamoTask.UpdateItem({
        tableName: "$.flightTable",
        key: "$.outboundFlightId",
        updateExpression: "SET seatAllocation = seatAllocation + :inc",
        expressionAttributeValues: {
          ":inc": dynamoTask.DynamoValue.fromNumber(1).value
        }
      }),
      timeout: cdk.Duration.seconds(5)
    })
      .addRetry({
        errors: [
          "ProvisionedThroughputExceededException",
          "RequestLimitExceeded",
          "ServiceUnavailable",
          "ThrottlingException"
        ],
        interval: cdk.Duration.seconds(1),
        backoffRate: 2,
        maxAttempts: 2
      })
      .addRetry({
        errors: ["ConditionalCheckFailedException"],
        interval: cdk.Duration.seconds(0),
        maxAttempts: 0
      });
  }

  private GetCancelBookingTask(): sfn.Task {
    const cancelBookingFunction = new lambda.Function(this, "CancelBooking", {
      code: lambda.Code.asset(
        path.resolve(
          __dirname,
          "..",
          "..",
          "booking",
          ".aws-sam",
          "build",
          "CancelBooking"
        )
      ),
      handler: "cancel.lambda_handler",
      runtime: lambda.Runtime.PYTHON_3_7
    });
    cancelBookingFunction.addToRolePolicy(
      DynamoDBCrudPolicy.forTable(this.props.BookingTable.Arn)
    );

    return new sfn.Task(this, "Cancel Booking", {
      task: new tasks.InvokeFunction(cancelBookingFunction)
    }).addRetry({
      errors: ["BookingCancellationException"],
      interval: cdk.Duration.seconds(1),
      backoffRate: 2,
      maxAttempts: 2
    });
  }

  private GetConfirmBookingTask(): sfn.Task {
    const confirmBookingFunction = new lambda.Function(this, "ConfirmBooking", {
      code: lambda.Code.asset(
        path.resolve(
          __dirname,
          "..",
          "..",
          "booking",
          ".aws-sam",
          "build",
          "ConfirmBooking"
        )
      ),
      handler: "confirm.lambda_handler",
      runtime: lambda.Runtime.PYTHON_3_7
    });
    confirmBookingFunction.addToRolePolicy(
      DynamoDBCrudPolicy.forTable(this.props.BookingTable.Arn)
    );

    return new sfn.Task(this, "Confirm Booking", {
      task: new tasks.InvokeFunction(confirmBookingFunction),
      resultPath: "$.bookingReference"
    }).addRetry({
      errors: ["BookingConfirmationException"],
      interval: cdk.Duration.seconds(1),
      backoffRate: 2,
      maxAttempts: 2
    });
  }

  private GetNotifyBookingTask(id: string, func: lambda.IFunction): sfn.Task {
    return new sfn.Task(this, "Notify Booking " + id, {
      task: new tasks.InvokeFunction(func),
      resultPath: "$.notificationId"
    }).addRetry({
      errors: ["BookingNotificationException"],
      interval: cdk.Duration.seconds(1),
      backoffRate: 2,
      maxAttempts: 2
    });
  }

  private GetReserveBookingTask(): sfn.Task {
    const reserveBookingFunction = new lambda.Function(this, "ReserveBooking", {
      code: lambda.Code.asset(
        path.resolve(
          __dirname,
          "..",
          "..",
          "booking",
          ".aws-sam",
          "build",
          "ReserveBooking"
        )
      ),
      handler: "reserve.lambda_handler",
      runtime: lambda.Runtime.PYTHON_3_7
    });
    reserveBookingFunction.addToRolePolicy(
      DynamoDBCrudPolicy.forTable(this.props.BookingTable.Arn)
    );

    return new sfn.Task(this, "Reserve Booking", {
      task: new tasks.InvokeFunction(reserveBookingFunction),
      resultPath: "$.bookingId"
    }).addRetry({
      errors: ["BookingReservationException"],
      interval: cdk.Duration.seconds(1),
      backoffRate: 2,
      maxAttempts: 2
    });
  }

  constructor(
    scope: cdk.Construct,
    id: string,
    private readonly props: BookingProps
  ) {
    super(scope, id);

    // Create Topic for notifications
    this.NotificationTopic = new sns.Topic(this, "Notifications");

    // Create Tasks for our imported functions
    this.CollectPaymentTask = new sfn.Task(this, "CollectPaymentTask", {
      task: new tasks.InvokeFunction(this.props.CollectPaymentFunction),
      resultPath: "$.payment"
    }).addRetry(this.GenericRetry);
    this.RefundPaymentTask = new sfn.Task(this, "RefundPaymentTask", {
      task: new tasks.InvokeFunction(this.props.RefundPaymentFunction)
    }).addRetry(this.GenericRetry);

    // Our DynamoDB Update Tasks
    this.ReserveFlightSeatTask = this.GetReserveFlightSeatTask();
    this.ReleaseFlightSeatTask = this.GetReleaseFlightSeatTask();

    // Our Lambda Function Tasks
    this.CancelBookingTask = this.GetCancelBookingTask();
    this.ConfirmBookingTask = this.GetConfirmBookingTask();
    this.ReserveBookingTask = this.GetReserveBookingTask();

    const notifyBookingFunction = new lambda.Function(this, "NotifyBooking", {
      code: lambda.Code.asset(
        path.resolve(
          __dirname,
          "..",
          "..",
          "booking",
          ".aws-sam",
          "build",
          "NotifyBooking"
        )
      ),
      handler: "reserve.lambda_handler",
      runtime: lambda.Runtime.PYTHON_3_7,
      environment: {
        BOOKING_TOPIC: this.NotificationTopic.topicName
      }
    });
    this.NotificationTopic.grantPublish(notifyBookingFunction);

    this.NotifyBookingFailedTask = this.GetNotifyBookingTask(
      "Failed",
      notifyBookingFunction
    );
    this.NotifyBookingSucceededTask = this.GetNotifyBookingTask(
      "Success",
      notifyBookingFunction
    );

    // End States
    this.BookingFailedState = new sfn.Fail(this, "Booking Failed", {
      comment: "Booking Failed"
    });
    this.BookingConfirmedState = new sfn.Pass(this, "Booking Confirmed", {
      comment: "Booking Confirmed"
    });

    /**
     * Now will join up the relevant states to build the error handling
     */
    this.ReserveFlightSeatTask.addCatch(this.NotifyBookingFailedTask, {
      resultPath: "$.flightError"
    });
    this.ReserveBookingTask.addCatch(this.CancelBookingTask, {
      resultPath: "$.bookingError"
    });
    this.ReleaseFlightSeatTask.addCatch(this.NotifyBookingFailedTask, {
      resultPath: "$.flightError"
    });
    this.CollectPaymentTask.addCatch(this.CancelBookingTask, {
      resultPath: "$.paymentError"
    });
    this.ConfirmBookingTask.addCatch(this.RefundPaymentTask, {
      resultPath: "$.bookingError"
    });

    // Build the error chain of nexts so the error path is built
    this.RefundPaymentTask.next(this.CancelBookingTask)
      .next(this.ReleaseFlightSeatTask)
      .next(this.NotifyBookingFailedTask)
      .next(this.BookingFailedState);

    // Now define the actual state machine
    new sfn.StateMachine(this, "Booking", {
      definition: this.ReserveFlightSeatTask.next(this.ReserveBookingTask)
        .next(this.CollectPaymentTask)
        .next(this.ConfirmBookingTask)
        .next(this.NotifyBookingSucceededTask)
        .next(this.BookingConfirmedState)
    });
  }
}
