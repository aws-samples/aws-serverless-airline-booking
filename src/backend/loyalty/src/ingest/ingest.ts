import { Context, SNSEvent } from 'aws-lambda';
import { DocumentClient } from 'aws-sdk/clients/dynamodb';
import uuidv4 from 'uuid/v4';

const dataTableName = process.env.DATA_TABLE_NAME;
const memberTableName = process.env.MEMBER_TABLE_NAME;

const client = new DocumentClient();

interface Result {
  message: string;
  loyalty?: LoyaltyPoints;
}

interface LoyaltyPoints {
  Id: string;
  CustomerId: string;
  Points: number;
  Date: string;
  Flag: LoyaltyStatus;
}

enum LoyaltyStatus {
  Active = "active",
  Revoked = "revoked",
  Expired = "expired"
}

interface LoyaltyMembership {
  CustomerId: string;
  MembershipId?: string;
}

export const handler = async (event: SNSEvent, context: Context): Promise<Result> => {
  console.log(memberTableName, dataTableName);
  if (!dataTableName || !memberTableName) {
    throw new Error(`Table name not set`);
  }

  const record = JSON.parse(event.Records[0].Sns.Message);
  const customerId = record['customerId'];
  const points = record['price'];

  let customer: LoyaltyMembership | undefined;

  try {
    await client.get({
      TableName: memberTableName,
      Key: {
        CustomerId: customerId
      }
    }, async (err, data) => {
      if (err) {
        throw err;
      }

      if (data.Item) {
        customer = {
          CustomerId: customerId,
          MembershipId: data.Item.MembershipId
        };
      } else {
        try {
          await client.put({
            TableName: memberTableName,
            Item: {
              CustomerId: customerId,
              MembershipId: uuidv4()
            }
          }).promise();
        } catch(err) {
          throw err;
        }
      
      }
    }).promise();
  } catch(err) {
    throw new Error(`GET: Unable to query table: ${memberTableName}: ${err}`);
  }

  const item: LoyaltyPoints = {
    Id: uuidv4(),
    CustomerId: customerId,
    Points: points,
    Flag: LoyaltyStatus.Active,
    Date: new Date().toISOString()
  };

  try {
    await client.put({
      TableName: dataTableName,
      Item: item as Object
    }).promise();
  } catch(e) {
    throw new Error(`Unable to write to DynamoDB: ${e}`);
  }

  return {
    message: "ok!",
    loyalty: item
  }
}