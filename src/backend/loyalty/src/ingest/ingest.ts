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
  user_id: string;
  points: number;
  date: string;
  flag: LoyaltyStatus;
  flight_id: string;
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
  const user_id = record['user_id'];
  const points = record['price'];
  const flight_id = record['flight_id'];

  const item: LoyaltyPoints = {
    id: '_' + Math.random().toString(36).substr(2, 9),
    user_id: user_id,
    points: points,
    flag: LoyaltyStatus.Active,
    date: new Date().toISOString(),
    flight_id: flight_id
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