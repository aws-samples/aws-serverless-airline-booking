
import { handler } from "./ingest"
import snsEvent from "./event.json"
import { SNSEvent, Context } from "aws-lambda"

describe('Loyalty Ingest Function tests', () => {
  test('should pass', () => { true });

  test('Successful write to Loyalty Table', async () => {

    process.env.TABLE_NAME = "loyalty-table";
    let event = snsEvent as SNSEvent
    let ctx = {} as Context

    // let mock = jest.fn().mockImplementation

    // mock = jest.fn().mockImplementation() {
    //   put: jest.fn(async () => true)
    // };

    const ret = await handler(event, ctx)

    console.log(ret)
    return true
  });
});
