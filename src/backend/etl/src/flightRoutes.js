const etlBucketName = process.env.ETL_BUCKET_NAME;
const flightsPerDay = process.env.FLIGHTS_PER_DAY;
const AWS = require('aws-sdk');
const Combinatorics = require('js-combinatorics');
const s3 = new AWS.S3();
const chunks = Math.ceil(flightsPerDay/2/10);

exports.create = async (event, context) => {

  if (!(event.execution && event.airportFileKey)){
    console.log("Missing parameters", event);
    throw new Error("Missing event parameters");
  }

  console.log("Retrieving file: ", event.airportFileKey);
  //Get airports file from S3
  const execution = event.execution;
  const response = await s3.getObject({
    Bucket: etlBucketName,
    Key: event.airportFileKey
  }).promise();

  const airports = JSON.parse(response.Body.toString('utf-8'));
  console.log("Number of airports: ", airports.length);

  //Generate flight routes by getting all possible combinations of airport pairs
  const allFlightRoutes = Combinatorics.bigCombination(airports,2).toArray();
  console.log("number of combinations: ", allFlightRoutes.length);

  //Reduce flight routes based on config
  const flightRoutes = allFlightRoutes.splice(0, flightsPerDay/2);
  console.log("number of flights per day: ", flightsPerDay);
  console.log("number of flight routes to upload: ", flightRoutes.length);
  console.log("Number of chunks", chunks);
  const routeChunks = chunkArray(flightRoutes, chunks);

  console.log("Uploading %i chunks to S3", routeChunks.length);
  const s3UploadRequests = routeChunks.map((chunk, i) => {
    const chunkFilename = `raw/${execution}/routes/${i}_routes.json`
    return s3.upload({
      Bucket: etlBucketName,
      Key: chunkFilename,
      Body: JSON.stringify(chunk)
    }).promise();
  });

  const results = await Promise.all(s3UploadRequests);
  console.log("Route chunks uploaded to S3: ", results);
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

