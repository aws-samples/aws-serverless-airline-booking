
import { addPoints } from "../src/ingest/ingest"

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
    // Environment Variable isn't being recognized by addPoints function
    process.env.DATA_TABLE_NAME = "loyalty-table";

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
