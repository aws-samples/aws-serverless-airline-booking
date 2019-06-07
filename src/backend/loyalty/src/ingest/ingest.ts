import { Context, SNSEvent } from 'aws-lambda';
import { DefaultDocumentClient, DocumentClientInterface } from './lib/document_client';
import uuidv4 from 'uuid/v4';

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
  Id: string;

  /**
   * Customer ID
   */
  CustomerId: string;

  /**
   * Points
   */
  Points: number;

  /**
   * DAte
   */
  Date: string;

  /**
   * Flag
   */
  Flag: LoyaltyStatus;
}

/**
 * Loyalty Status
 */
enum LoyaltyStatus {
  /**
   * Active
   */
  Active = "active",

  /**
   * Revoked
   */
  Revoked = "revoked",

  /**
   * Expired
   */
  Expired = "expired"
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
      Id: uuidv4(),
      CustomerId: customerId,
      Points: points,
      Flag: LoyaltyStatus.Active,
      Date: new Date().toISOString()
    };

    let params = {
      TableName: tableName,
      Item: item as Object
    }

    try {
      await client.put(params).promise();
    } catch (e) {
      throw new Error(`Unable to write to DynamoDB: ${e}`);
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
export const handler = async (event: SNSEvent, context: Context): Promise<Result> => {
  if (!table) {
    throw new Error(`Table name not defined`);
  }

  try {
    const record = JSON.parse(event.Records[0].Sns.Message);
    const customerId = record['customerId'];
    const points = record['price'];

    await addPoints(customerId, points, client, table)
  } catch (error) {
    throw error
  }

  return {
    message: "ok!",
  }
}