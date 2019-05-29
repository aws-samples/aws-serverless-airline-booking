import { APIGatewayEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DocumentClient, ItemList } from 'aws-sdk/clients/dynamodb';

const dataTableName = process.env.DATA_TABLE_NAME;
const client = new DocumentClient();

interface Result {
  Points: number;
  Level: string;
}

export const handler = async (event: APIGatewayEvent): Promise<APIGatewayProxyResult> => {
  if (!event.pathParameters || !event.pathParameters.CustomerId) {
    throw new Error('CustomerId not defined');
  }

  if (!dataTableName) {
    throw new Error('Table name is undefined');
  }

  const customerId = event.pathParameters.CustomerId;

  let items: ItemList = [];

  await client.query({
    TableName: dataTableName,
    IndexName: "customer-flag",
    KeyConditionExpression: 'CustomerId = :hkey and Flag = :rkey',
    ExpressionAttributeValues: {
      ':hkey': customerId,
      ':rkey': 'active'
    }
  }, function (err, data) {
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
    console.log(v.Points);
    points = points + (v.Points as number);
  }

  const result: Result = {
    Points: points,
    Level: level(points)
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