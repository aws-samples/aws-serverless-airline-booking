import { APIGatewayEvent, APIGatewayProxyResult, APIGatewayEventRequestContext } from 'aws-lambda';
import * as aws from 'aws-sdk';

const tableName = process.env.TABLE_NAME;
const client = new aws.DynamoDB.DocumentClient();

export const handler = async (event: APIGatewayEvent, context: APIGatewayEventRequestContext): Promise<APIGatewayProxyResult> => {
  if (!event.pathParameters || !event.pathParameters.user_id) {
    throw new Error('user_id not defined');
  }

  if (!tableName) {
    throw new Error('Table name is undefined');
  }

  const user_id = event.pathParameters.user_id;

  let zomg: Object = {};

  await client.query({
    TableName: tableName,
    IndexName: "user-flag",
    KeyConditionExpression: 'user_id = :hkey and flag = :rkey',
    ExpressionAttributeValues: {
      ':hkey': user_id,
      ':rkey': 'active'
    }
  }, function(err , data) { zomg = data }).promise();

  return {
    statusCode: 200,
    body: JSON.stringify(zomg)
  };
}