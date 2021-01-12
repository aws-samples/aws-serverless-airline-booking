import { Context, SNSEvent } from 'aws-lambda';
import { DefaultDocumentClient, DocumentClientInterface, PutInput } from './lib/document_client';
// import uuidv4 from 'uuid/v4';
import { v4 as uuidv4 } from 'uuid';

const client = DefaultDocumentClient;
const table = process.env.TABLE_NAME

/**
 * Result interface
 */
interface Result {
  /**
   * Message
   */
  message: string;
}

/**
 * LoyaltyPoints interface
 */
interface LoyaltyPoints {
  /**
   * Identifier
   */
  id: string;

  /**
   * Customer ID
   */
  customerId: string;

  /**
   * Points
   */
  points: number;

  /**
   * DAte
   */
  date: string;

  /**
   * Flag
   */
  flag: LoyaltyStatus;
}

/**
 * Loyalty Status
 */
enum LoyaltyStatus {
  /**
   * Active
   */
  active = "active",

  /**
   * Revoked
   */
  revoked = "revoked",

  /**
   * Expired
   */
  expired = "expired"
}

/**
 * Add loyalty points to a given customerID
 *
 * @param {string} customerId - customer unique identifier
 * @param {number} points - points that should be added to the customer
 * @param {DocumentClient} dynamo - AWS DynamoDB DocumentClient
 */
export const addPoints = async (customerId: string, points: number, client: DocumentClientInterface, tableName: string) => {
  const item: LoyaltyPoints = {
    id: uuidv4(),
    customerId: customerId,
    points: points,
    flag: LoyaltyStatus.active,
    date: new Date().toISOString()
  };

  let params: PutInput = {
    TableName: tableName,
    Item: item as Object
  }

  try {
    await client.put(params).promise();
  } catch (error) {
    console.log(error);
    throw new Error(`Unable to write to DynamoDB`);
  }
}


/**
 * Lambda Function handler that takes one SNS message at a time and add loyalty points to a customer
 * While SNS does send records in an Array it only has one event
 * That means we're safe to only select the first one (event.records[0])
 *
 * @param {SNSEvent} event
 * @param {Context} context
 * @returns {Promise<Result>}
 */
export async function handler(event: SNSEvent, context: Context): Promise<Result> {

  if (!table) {
    throw new Error(`Table name not defined`);
  }

  try {
    const record = JSON.parse(event.Records[0].Sns.Message);
    const customerId = record['customerId'];
    const points = record['price'];

    if (isNaN(points)) {
      throw new Error("Points cannot be undefined or falsy")
    }

    await addPoints(customerId, points, client, table)
  } catch (error) {
    if (error instanceof SyntaxError) {
      console.log(event);
      throw new Error("Invalid input");
    }

    throw error
  }

  return {
    message: "ok!",
  }
}