const etlBucketName = process.env.ETL_BUCKET_NAME;
const AWS = require('aws-sdk');
const Combinatorics = require('js-combinatorics');
const s3 = new AWS.S3();
const chunks = 10;

let response;

exports.create = async (event, context) => {
  console.log(event);

  const execution = event.execution;
  const response = await s3.getObject({
    Bucket: etlBucketName,
    Key: event.airportFileKey
  }).promise();

  const airports = JSON.parse(response.Body.toString('utf-8'));
  console.log(airports.length);

  const flightRoutes = Combinatorics.bigCombination(airports,2).toArray();
  console.log("number of combinations: ", flightRoutes.length);
  const routeChunks = chunkArray(flightRoutes, chunks);
  console.log(routeChunks.length);

  console.log("Uploading chunks to S3");
  const s3UploadRequests = routeChunks.map((chunk, i) => {
    const chunkFilename = `raw/${execution}/routes/${i}_routes.json`
    return s3.upload({
      Bucket: etlBucketName,
      Key: chunkFilename,
      Body: JSON.stringify(chunk)
    }).promise();
  });

  const results = await Promise.all(s3UploadRequests);
  console.log(results);
  return results;
};

function chunkArray(arr, chunkCount) {
  const chunks = [];
  while(arr.length) {
    const chunkSize = Math.ceil(arr.length / chunkCount--);
    const chunk = arr.slice(0, chunkSize);
    chunks.push(chunk);
    arr = arr.slice(chunkSize);
  }
  return chunks;
}

