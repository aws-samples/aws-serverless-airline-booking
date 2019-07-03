import DynamoDB, { DocumentClient } from 'aws-sdk/clients/dynamodb';
import { PutInput } from '../../src/ingest/lib/document_client';

interface Credentials {
  accessKeyId: string,
  secretAccessKey: string,
  sessionToken: string
}

export async function getDbInstance(credentials:Credentials|undefined): Promise<DynamoDB> {
  return new DynamoDB(credentials);
}

export async function createTable(tableName: string, dynamoDb: DynamoDB): Promise<Object> {
  const params = {
    AttributeDefinitions: [{
      AttributeName: 'customerId',
      AttributeType: 'S'
    },
    {
      AttributeName: 'flag',
      AttributeType: 'S'
    },
    {
      AttributeName: 'id',
      AttributeType: 'S'
    }],
    KeySchema: [{
      AttributeName: "id",
      KeyType: "HASH"
    }],
    GlobalSecondaryIndexes: [{
      IndexName: 'customer-flag',
      KeySchema: [{
        AttributeName: 'customerId',
        KeyType: 'HASH'
      },
      {
        AttributeName: 'flag',
        KeyType: 'RANGE'
      }],
      Projection: {
        ProjectionType: 'ALL'
      }
    }],
    BillingMode: 'PAY_PER_REQUEST',
    TableName: tableName
  };
  await dynamoDb.createTable(params).promise();

  return dynamoDb.waitFor('tableExists', {
    TableName: tableName
  }).promise();
}

export async function deleteTable(tableName: string, dynamoDb: DynamoDB): Promise<Object> {
  // Destroy a table at the end of our tests
  return await dynamoDb.deleteTable({
    TableName: tableName
  }).promise();
}

export async function insertData(tableName: string, data: Object, docClient: DocumentClient): Promise<Object> {
  const params: PutInput = {
    TableName: tableName,
    Item: data
  };
  return await docClient.put(params).promise();
}