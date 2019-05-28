import { APIGatewayEvent, APIGatewayProxyResult, APIGatewayEventRequestContext } from 'aws-lambda';
import * as aws from 'aws-sdk';

const tableName = process.env.TABLE_NAME;
const client = new aws.DynamoDB.DocumentClient();

interface Result {
  Points: number;
  level: string;
}

export const handler = async (event: APIGatewayEvent, context: APIGatewayEventRequestContext): Promise<APIGatewayProxyResult> => {
  if (!event.pathParameters || !event.pathParameters.user_id) {
    throw new Error('user_id not defined');
  }

  if (!tableName) {
    throw new Error('Table name is undefined');
  }

  const user_id = event.pathParameters.user_id;

  let items: aws.DynamoDB.DocumentClient.ItemList = [];

  await client.query({
    TableName: tableName,
    IndexName: "user-flag",
    KeyConditionExpression: 'user_id = :hkey and flag = :rkey',
    ExpressionAttributeValues: {
      ':hkey': user_id,
      ':rkey': 'active'
    }
  }, function(err , data) { 
    if (err) {
      throw new Error(`Unable to query data`);
    }
    if (data.Items) {
      items = data.Items;
    } else {
      throw new Error(`No data returned`);
    }
  }).promise();

  let points = 0;

  for (let v of items) {
    points += v.points;
  }

  const result = {
    points: points,
    level: level(points)
  }

  return {
    statusCode: 200,
    body: JSON.stringify(result as Object)
  };

}

const level = (points: number): string => {
  switch (true) {
    case (points > 100000):
      return "gold";
    case (points > 50000 && points < 100000):
      return "silver"
    default:
      return "bronze";
  }
}