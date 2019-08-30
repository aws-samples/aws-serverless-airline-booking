const etlBucketName = process.env.ETL_BUCKET_NAME;
const flightsTable = process.env.FLIGHTS_TABLE_NAME;

const AWS = require('aws-sdk');
const s3 = new AWS.S3();
const ddb = new AWS.DynamoDB.DocumentClient();


exports.addToDatabase = async (event, context) => {
  console.log(event);
  const execution = event.execution;
  const index = event.index;

  const response = await s3.getObject({
    Bucket: etlBucketName,
    Key: event.flightsFileKey
  }).promise();

  let flights = JSON.parse(response.Body.toString('utf-8'));
  console.log(flights.length);

  const putRequests = flights.map((flight) => {
    return ddb.put({
      TableName: flightsTable,
      Item: flight
    }).promise();
  });

  return await Promise.all(putRequests);
}