/*
  Environment variables:
  - `LOYALTY_INTEG_ROLE` (optional): Arn for an existing role that will be assumed in integration tests
  - `DYNAMODB_TABLE` (optional): Provide the name of an existing DynamoDB table to speed up the tests
  - `QUERY_TIMEOUT` (optional): A timeout in milliseconds between writing data to the table and running a query, because of eventual consitency of queries on global secondary indexes
*/
import DynamoDB, { DocumentClient } from 'aws-sdk/clients/dynamodb';
import { getCredentials } from './helpers/credentials-helper';
import { getDbInstance, createTable, deleteTable, insertData } from './helpers/dynamodb-helper';
import { wait } from './helpers/timeout-helper';
import uuidv4 from 'uuid/v4';

import { addPoints } from '../src/ingest';
import { points } from '../src/get';

let dynamoDb:DynamoDB, documentClient:DocumentClient;

// Table name for test DynamoDB
const tableName = process.env.DYNAMODB_TABLE ? process.env.DYNAMODB_TABLE : `airline-test-table-${uuidv4()}`;
// Query timeout
const queryTimeout: number = process.env.QUERY_TIMEOUT ? parseInt(process.env.QUERY_TIMEOUT, 10) : 200;

describe('integration', () => {
  beforeAll(async () => {
    let credentials;
    // If LOYALTY_INTEG_ROLE is provided, assume it
    if (process.env.LOYALTY_INTEG_ROLE !== undefined) {
      credentials = await getCredentials(process.env.LOYALTY_INTEG_ROLE, process.env.LOYALTY_INTEG_EXTERNAL_ID);
    }

    // Initialize DynamoDB instance with assumed role or default credentials
    dynamoDb = await getDbInstance(credentials);

    // Initialize document client with assumed role or default credentials
    documentClient = new DocumentClient(credentials);

    // If the existing DynamoDB table is not provided
    if (!process.env.DYNAMODB_TABLE) {
      // Create a new DynamoDB table
      return await createTable(tableName, dynamoDb);
    }

    // Otherwise return a promise
    return Promise.resolve();
  }, 90000); // Increase the timeout for `beforeAll` to 90s, because deleting table takes time

  afterAll(async () => {
    // If the existing DynamoDB table is not provided
    if (!process.env.DYNAMODB_TABLE) {
      // Delete the DynamoDB table used for testing
      return await deleteTable(tableName, dynamoDb);
    }
  }, 90000); // Increase the timeout for `afterAll` to 90s, because deleting table takes time

  describe('ingest', () => {
    test('should write to loyalty table', async () => {
      const customerId = uuidv4();
      await addPoints(customerId, 1235, documentClient, tableName);

      // A short delay, because of eventual consitency of queries on global secondary indexes
      await wait(queryTimeout);
      
      const params = {
        TableName: tableName,
        IndexName: "customer-flag",
        KeyConditionExpression: 'customerId = :hkey and flag = :rkey',
        ExpressionAttributeValues: {
          ':hkey': customerId,
          ':rkey': 'active'
        }
      };
      
      const result = await documentClient.query(params).promise();
      
      expect(Array.isArray(result.Items)).toBeTruthy();
      expect(result.Items!.length).toBe(1);
      expect(result.Items![0].customerId).toBe(customerId);
    });
    
    test('should write multiple entries for the same customer id', async () => {
      const customerId = uuidv4();
      await addPoints(customerId, 100, documentClient, tableName);
      await addPoints(customerId, 200, documentClient, tableName);
      
      await wait(queryTimeout);
      
      const params = {
        TableName: tableName,
        IndexName: "customer-flag",
        KeyConditionExpression: 'customerId = :hkey and flag = :rkey',
        ExpressionAttributeValues: {
          ':hkey': customerId,
          ':rkey': 'active'
        }
      };
      
      const result = await documentClient.query(params).promise();
      
      expect(Array.isArray(result.Items)).toBeTruthy();
      expect(result.Items!.length).toBe(2);
      expect(result.Items![0].points + result.Items![1].points).toBe(300);
    });
  });
  
  describe('get', () => {
    test('should throw the "no data" error if no entries were found', async () => {
      const customerId = uuidv4();
      try {
        await points(customerId, documentClient, tableName);
      } catch (err) {
        expect(err).toContain('No data');
      }
    });

    test('should return points for a single found entry', async () => {
      const customerId = uuidv4();
      const data = {
        id: uuidv4(),
        customerId: customerId,
        points: 100,
        flag: 'active',
        date: new Date().toISOString()
      };
      await insertData(tableName, data, documentClient);

      await wait(queryTimeout);

      const numberOfPoints = await points(customerId, documentClient, tableName);
      expect(numberOfPoints).toBe(100);
    });

    test('should return a sum of points for all entries', async () => {
      const customerId = uuidv4();
      await Promise.all([100, 200, 300].map(points => {
        const data = {
          id: uuidv4(),
          customerId: customerId,
          points: points,
          flag: 'active',
          date: new Date().toISOString()
        };
        return insertData(tableName, data, documentClient);
      }));

      await wait(queryTimeout);

      const numberOfPoints = await points(customerId, documentClient, tableName);
      expect(numberOfPoints).toBe(600);
    });
  });

  describe('ingest and get integration', () => {
    test('should insert an entry using ingest and read them using get', async () => {
      const customerId = uuidv4();
      await addPoints(customerId, 1235, documentClient, tableName);

      await wait(queryTimeout);

      const numberOfPoints = await points(customerId, documentClient, tableName);
      expect(numberOfPoints).toBe(1235);
    });

    test('should insert an entry using ingest and read them using get', async () => {
      const customerId = uuidv4();
      await Promise.all([100, 200, 300].map(points => {
        return addPoints(customerId, points, documentClient, tableName);
      }));

      await wait(queryTimeout);

      const numberOfPoints = await points(customerId, documentClient, tableName);
      expect(numberOfPoints).toBe(600);
    });
  });

});
