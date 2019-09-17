const etlBucketName = process.env.ETL_BUCKET_NAME;
const flightsTable = process.env.FLIGHTS_TABLE_NAME;

const AWS = require('aws-sdk');
const s3 = new AWS.S3();
const ddb = new AWS.DynamoDB.DocumentClient();


exports.addToDatabase = async (event, context) => {

  if (!(event.execution && event.flightsFileKey && Number.isInteger(event.index))){
    console.log("Missing parameters", event);
    throw new Error("Missing event parameters");
  }

  const execution = event.execution;
  const index = event.index;

  console.log("Retrieving Flights file: ", event.flightsFileKey);
  const response = await s3.getObject({
    Bucket: etlBucketName,
    Key: event.flightsFileKey
  }).promise();

  let flights = JSON.parse(response.Body.toString('utf-8'));
  console.log("Total number of flights to add: ", flights.length);

  //TODO use BatchWrite to batch writes by 25 records
  const putRequests = flights.map((flight) => {
    return ddb.put({
      TableName: flightsTable,
      Item: flight
    }).promise();
  });

  const ddbResults = await Promise.all(putRequests);

  return {
    flightsAdded: flights.length,
    flightsFileKey: event.flightsFileKey
  };
}