import * as AWSMock from 'aws-sdk-mock';
import * as AWS from 'aws-sdk';
import { points } from '../src/get';
import { QueryInput } from "../src/get/lib/document_client"

describe('Loyalty Ingest Function tests', () => {
  beforeEach(() => {
    jest.resetModules()
  });

  test('Successful read from Loyalty Table', async () => {
    AWSMock.setSDKInstance(AWS);
    AWSMock.mock('DynamoDB.DocumentClient', 'query', (params: QueryInput, callback: Function) => {
      callback(null, {
        Items: [
          { customerId: 'hooman', points: 500 }
        ]
      });
    })

    const doc = new AWS.DynamoDB.DocumentClient();
    const ret = await points('hooman', doc, 'loyalty-table');

    expect(ret).toEqual(500);
  });

  test('No data read from Loyalty Table', async () => {
    AWSMock.setSDKInstance(AWS);
    AWSMock.mock('DynamoDB.DocumentClient', 'query', (params: QueryInput, callback: Function) => {
      callback(null, {});
    })

    const doc = new AWS.DynamoDB.DocumentClient();

    try {
      await points('hooman', doc, 'loyalty-table');
    } catch (err) {
      expect(err).toContain('No data')
    }
  });
});
