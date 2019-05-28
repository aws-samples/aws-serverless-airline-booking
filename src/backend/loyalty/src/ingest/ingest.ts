import { Context, SNSEvent } from 'aws-lambda';
import * as aws from 'aws-sdk';

const tableName = process.env.TABLE_NAME;
const client = new aws.DynamoDB.DocumentClient();

interface Result {
  message: string;
  loyalty?: LoyaltyPoints;
}

interface LoyaltyPoints {
  id: string;
  customerId: string;
  points: number;
  date: string;
  flag: LoyaltyStatus;
}

enum LoyaltyStatus {
  Active = "active",
  Revoked = "revoked",
  Expired = "expired"
}

export const handler = async (event: SNSEvent, context: Context): Promise<Result> => {
  console.log(tableName);
  if (!tableName) {
    throw new Error(`Table name not set`);
  }

  const record = JSON.parse(event.Records[0].Sns.Message);
  const customerId = record['customerId'];
  const points = record['price'];

  const item: LoyaltyPoints = {
    id: '_' + Math.random().toString(36).substr(2, 9),
    customerId: customerId,
    points: points,
    flag: LoyaltyStatus.Active,
    date: new Date().toISOString()
  };

  await client.put({
    TableName: tableName,
    Item: item as Object
  }).promise();

  return {
    message: "ok!",
    loyalty: item
  }
}