import * as AWSMock from "aws-sdk-mock";
import * as AWS from "aws-sdk"; 
import { points } from "../src/get/get";

describe('Loyalty Ingest Function tests', () => {
  beforeEach(() => {
    jest.resetModules()
  });

  test('Successful read from Loyalty Table', async () => {
    AWSMock.setSDKInstance(AWS);
    AWSMock.mock('DynamoDB.DocumentClient', 'query', (params: AWS.DynamoDB.DocumentClient.QueryInput, callback: Function) => {
      callback(null, {Items: [
        {CustomerId: "hooman", Points: 500}
      ]});
    })

    const doc = new AWS.DynamoDB.DocumentClient();

    // Assume if there's no Exception it worked.
    const ret = await points("hooman", doc, 'loyalty-table');

    expect(ret).toEqual(500);
  });
});
