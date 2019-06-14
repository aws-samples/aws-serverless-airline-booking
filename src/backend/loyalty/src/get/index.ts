import { APIGatewayEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DefaultDocumentClient, DocumentClientInterface, QueryInput, ItemList } from './lib/document_client';

const tableName = process.env.TABLE_NAME;
const client = DefaultDocumentClient;

/**
 * Result interface
 */
interface Result {
  /**
   * Points
   */
  points: number;

  /**
   * Level
   */
  level: string;
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
  let params: QueryInput = {
    TableName: tableName,
    IndexName: "customer-flag",
    KeyConditionExpression: 'customerId = :hkey and flag = :rkey',
    ExpressionAttributeValues: {
      ':hkey': customerId,
      ':rkey': 'active'
    }
  }

  try {
    let data = await client.query(params).promise()
    if (data.Items) {
      items = data.Items
    }
  } catch (error) {
    console.log(error);
    throw new Error(`Unable to query data`);
  }

  let points = 0;

  for (let v of items) {
    points = points + (v.points as number);
  }

  return points;
};

/**
 * Lambda function handler that takes a HTTP event from API GW
 * 
 * @param {APIGatewayEvent} event
 * @returns {Promise<APIGatewayProxyResult>}
 */
export const handler = async (event: APIGatewayEvent): Promise<APIGatewayProxyResult> => {
  if (!event.pathParameters || !event.pathParameters.customerId) {
    throw new Error('customerId not defined');
  }

  if (!tableName) {
    throw new Error('Table name is undefined');
  }

  const customerId = event.pathParameters.customerId;

  let p: number;
  try {
    p = await points(customerId, client, tableName)
  } catch (err) {
    console.log(err);
    throw err;
  }

  const result: Result = {
    points: p,
    level: level(p)
  }

  return {
    statusCode: 200,
    body: JSON.stringify(result as Object)
  };
}