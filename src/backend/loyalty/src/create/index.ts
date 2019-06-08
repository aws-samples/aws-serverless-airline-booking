import { APIGatewayEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DocumentClient } from 'aws-sdk/clients/dynamodb';
import uuidv4 from 'uuid/v4';

const memberTableName = process.env.MEMBER_TABLE_NAME;
const client = new DocumentClient();

interface LoyaltyAccount {
  CustomerId: string;
  MembershipId?: string;
}

export const handler = async (event: APIGatewayEvent): Promise<APIGatewayProxyResult> => {
  if (!event.body) {
    throw new Error(`Body is undefined`);
  }

  const body = JSON.parse(event.body);
  const payload: LoyaltyAccount = {
    CustomerId: body.customerId
  };

  if (!memberTableName) {
    throw new Error(`Table name is undefined ${memberTableName}`);
  }

  let count = 0;

  try {
    await client.get({
      TableName: memberTableName,
      Key: {
        CustomerId: payload.CustomerId
      }
    }, (err, data) => {
      if (err) {
        throw err;
      }

      if (data.Item) {
        count++;
      }
    }).promise();
  } catch(err) {
    throw new Error(`GET: Unable to query table: ${memberTableName}: ${err}`);
  }

  if (count > 0) {
    return {
      statusCode: 409,
      body: JSON.stringify({
        message: "customer is already a member"
      })
    };
  }

  payload.MembershipId = uuidv4();

  try {
    await client.put({
      TableName: memberTableName,
      Item: payload as Object
    }).promise();
  } catch(err) {
    throw err;
  }

  return {
    statusCode: 201,
    body: JSON.stringify({
      message: `Created membership for ${payload.CustomerId}`
    })
  };
}