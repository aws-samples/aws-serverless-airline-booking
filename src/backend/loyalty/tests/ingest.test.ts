import * as AWSMock from 'aws-sdk-mock';
import * as AWS from 'aws-sdk';
import { addPoints } from '../src/ingest';
import { PutInput } from '../src/ingest/lib/document_client';


describe('Loyalty Ingest Function tests', () => {
  beforeEach(() => {
    jest.resetModules()
  });

  test('Successful write to Loyalty Table', async () => {
    AWSMock.setSDKInstance(AWS);
    AWSMock.mock('DynamoDB.DocumentClient', 'put', (params: PutInput, callback: Function) => {
      callback(null, { pk: 'foo', sk: 'bar' });
    })

    const doc = new AWS.DynamoDB.DocumentClient();

    // Assume if there's no Exception it worked.
    const ret = await addPoints('hooman', 1235, doc, 'loyalty-table');
  });
});
