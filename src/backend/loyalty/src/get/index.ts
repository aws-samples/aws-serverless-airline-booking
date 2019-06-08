import { APIGatewayEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DefaultDocumentClient, DocumentClientInterface } from './lib/document_client';
import { ItemList } from 'aws-sdk/clients/dynamodb';

const tableName = process.env.DATA_TABLE_NAME;
const client = DefaultDocumentClient;

/**
 * Result interface
 */
interface Result {
  /**
   * Points
   */
  Points: number;

  /**
   * Level
   */
  Level: string;
}

/**
 * Calculate the level based on number of points
 * 
 * @param points number
 * @returns string
 */
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

/**
 * Returns the number of points for a customer
 * 
 * @param {string} customerId
 * @param {DocumentClientInterface} client
 * @param {string} tableName
 * @returns {Promise<number>}
 */
export const points = async (customerId: string, client: DocumentClientInterface, tableName: string): Promise<number> => {
  let items: ItemList = [];

  await client.query({
    TableName: tableName,
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

  let p = 0;

  for (let v of items) {
    p = p + (v.Points as number);
  }

  return p;
};

/**
 * Lambda function handler that takes a HTTP event from API GW
 * 
 * @param {APIGatewayEvent} event
 * @returns {Promise<APIGatewayProxyResult>}
 */
export const handler = async (event: APIGatewayEvent): Promise<APIGatewayProxyResult> => {
  if (!event.pathParameters || !event.pathParameters.CustomerId) {
    throw new Error('CustomerId not defined');
  }

  if (!tableName) {
    throw new Error('Table name is undefined');
  }

  const customerId = event.pathParameters.CustomerId;

  let p: number;
  try {
    p = await points(customerId, client, tableName)
  } catch(err) {
    throw err;
  }

  const result: Result = {
    Points: p,
    Level: level(p)
  }

  return {
    statusCode: 200,
    body: JSON.stringify(result as Object)
  };
}