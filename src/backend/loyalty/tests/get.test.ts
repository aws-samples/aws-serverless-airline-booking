import * as AWSMock from 'aws-sdk-mock';
import * as AWS from 'aws-sdk';
import { points, nextTier, LoyaltyTier, level } from '../src/get';
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

  test('Test next tier implementation', async () => {

    let points: number = 100
    let result = nextTier(points, LoyaltyTier.bronze)
    let bronze2SilverPoints: number = 49900

    expect(result).toBe(bronze2SilverPoints)

    let silver2GoldPoints: number = 99900
    result = nextTier(points, LoyaltyTier.silver)

    expect(result).toBe(silver2GoldPoints)

    let gold2Next: number = 0
    result = nextTier(points, LoyaltyTier.gold)
  });

  test('Test level implementation', async () => {

    let points: number = 100
    let result = level(points)
    expect(result).toBe(LoyaltyTier.bronze)

    points = 50000
    result = level(points)
    expect(result).toBe(LoyaltyTier.silver)

    points = 200000
    result = level(points)
    expect(result).toBe(LoyaltyTier.gold)
  });
});
