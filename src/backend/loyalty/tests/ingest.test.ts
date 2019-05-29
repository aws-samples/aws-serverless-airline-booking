
import { addPoints } from "../src/ingest/ingest"
import snsEvent from "../src/ingest/event.json"
import { SNSEvent, Context } from "aws-lambda"

describe('Loyalty Ingest Function tests', () => {

  // Retrieve entire environment variables
  // and reset it before each test (clear test cache and env vars)
  const OLD_ENV = process.env;

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...OLD_ENV };
    delete process.env.NODE_ENV;
  });

  test('Successful write to Loyalty Table', async () => {

    // TODO: How do I make this work? ;)
    process.env.DATA_TABLE_NAME = "loyalty-table";

    let event = snsEvent as SNSEvent
    let ctx = {} as Context

    const clientStub = {
      put: () => {
          return {
            promise: () => Promise.resolve(true)
          }
      }
    }

    // Assume if there's no Exception it worked.
    const ret = await addPoints("hooman", 1235, clientStub)
  });
});
