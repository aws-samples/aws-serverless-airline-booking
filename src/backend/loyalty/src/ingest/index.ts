import { Context, SNSEvent } from 'aws-lambda';
import { DocumentClient } from 'aws-sdk/clients/dynamodb';
import uuidv4 from 'uuid/v4';

const client = new DocumentClient();

interface Result {
  message: string;
  loyalty?: LoyaltyPoints;
}

interface LoyaltyPoints {
  Id: string;
  CustomerId: string;
  Points: number;
  Date: string;
  Flag: LoyaltyStatus;
}

enum LoyaltyStatus {
  Active = "active",
  Revoked = "revoked",
  Expired = "expired"
}


export /**
 * Add loyalty points to a given customerID
 *
 * @param {string} customerId - customer unique identifier
 * @param {number} points - points that should be added to the customer
 * @param {DocumentClient} dynamo - AWS DynamoDB DocumentClient
 */
  const addPoints = async (customerId: string, points: number, document: any) => {

    const dataTableName: string | undefined = process.env.DATA_TABLE_NAME;

    if (!dataTableName) {
      throw new Error(`Table name not set`);
    }

    const item: LoyaltyPoints = {
      Id: uuidv4(),
      CustomerId: customerId,
      Points: points,
      Flag: LoyaltyStatus.Active,
      Date: new Date().toISOString()
    };

    let params = {
      TableName: dataTableName,
      Item: item as Object
    }

    try {
      await document.put(params).promise();
    } catch (e) {
      throw new Error(`Unable to write to DynamoDB: ${e}`);
    }
  }


export /**
 * Lambda Function handler that takes one SNS message at a time and add loyalty points to a customer
 * While SNS does send records in an Array it only has one event
 * That means we're safe to only select the first one (event.records[0])
 *
 * @param {SNSEvent} event
 * @param {Context} context
 * @returns {Promise<Result>}
 */
  const handler = async (event: SNSEvent, context: Context): Promise<Result> => {

    console.log("Running in SAM CLI....")

    try {
      const record = JSON.parse(event.Records[0].Sns.Message);
      const customerId = record['customerId'];
      const points = record['price'];

      // await addPoints(customerId, points, client)
    } catch (error) {
      throw error
    }

    return {
      message: "ok!",
    }
  }