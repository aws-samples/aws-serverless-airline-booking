const airports =  require("./data/airports.json");
const etlBucketName = process.env.ETL_BUCKET_NAME;
const AWS = require('aws-sdk');
const s3 = new AWS.S3();

let response;

exports.add = async (event, context) => {
  console.log(event);

  const execution = event.execution;
  const validAirports = airports.filter(airport => (airport.code && airport.country && airport.city && airport.name));
  console.log("Number of airports from file: ", airports.length);
  console.log("Number of valid airports: ", validAirports.length);
  const s3FileName = `raw/${execution}/airports/airports.json`;
  console.log("Uploading to S3: ", s3FileName);

  const result = await uploadAirportData(etlBucketName, s3FileName, validAirports);
  console.log("File uploaded: ",result);

  return {
    airportFileKey: s3FileName
  };
};

// upload Cleaned file to S3
function uploadAirportData(etlBucketName, s3FileName, validAirports){
  const params = {
    Bucket: etlBucketName,
    Key: s3FileName,
    Body: JSON.stringify(validAirports)
  };
  return s3.upload(params).promise();
}


