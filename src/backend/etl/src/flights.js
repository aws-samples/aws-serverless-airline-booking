const etlBucketName = process.env.ETL_BUCKET_NAME;
const AWS = require('aws-sdk');
const faker = require('faker');
const moment = require('moment');
const s3 = new AWS.S3();


exports.generate = async (event, context) => {

  if (!(event.execution && event.routeFileKey && Number.isInteger(event.index))){
    console.log("Missing parameters", event);
    throw new Error("Missing event parameters");
  }

  const execution = event.execution;
  const index = event.index;
  console.log("Retrieving Route file: ", event.routeFileKey);
  const response = await s3.getObject({
    Bucket: etlBucketName,
    Key: event.routeFileKey
  }).promise();

  let routes = JSON.parse(response.Body.toString('utf-8'));
  console.log("Number of routes to process: ", routes.length);

  //for each route
  const allFlights = routes.map(route => generateFlights(route))
                           .reduce((arr, x) => arr.concat(x), []); //flatten array

  console.log("Generated flights for chunk %i: %i", index, allFlights.length);
  //write the file
  const chunkFilename = `raw/${execution}/flights/${index}_flights.json`;
  console.log("Uploading file to S3: ", chunkFilename);
  return s3.upload({
    Bucket: etlBucketName,
    Key: chunkFilename,
    Body: JSON.stringify(allFlights)
  }).promise();
};



function generateFlights(route){
  const airport1 = route[0];
  const airport2 = route[1];

  // Create for the next 30 days
  const next30Days = [...Array(30)].map((x, i) => {
    const start = moment().utc().add(i+1, 'days').startOf('day').toDate();
    const end = moment().utc().add(i+1, 'days').endOf('day').toDate();

    const outboundFlight = createFlight(airport1, airport2, start, end);
    const inboundFlight = createFlight(airport2, airport1, start, end);

    return [outboundFlight, inboundFlight];
  }).reduce((arr, x) => arr.concat(x), []); //flatten array

  return next30Days;
}

function createFlight(departureAirport, arrivalAirport, start, end){
  const flightDeparture = getRandomDate(start, end);
  const flightArrival = getRandomDate(flightDeparture, end);
  const availableSeats = Math.floor(Math.random() * Math.floor(50)) + 1;
  const flight = {
    id: faker.random.uuid(),
    "arrivalAirportCode#departureDate": arrivalAirport.code+"#"+flightDeparture.toISOString(),
    departureDate: flightDeparture,
    departureAirportCode: departureAirport.code,
    departureAirportName: departureAirport.name,
    departureCity: departureAirport.city,
    departureLocale: faker.random.locale(),
    arrivalDate: flightArrival,
    arrivalAirportCode: arrivalAirport.code,
    arrivalAirportName: arrivalAirport.name,
    arrivalCity: arrivalAirport.city,
    arrivalLocale: faker.random.locale(),
    ticketPrice: parseInt(faker.finance.amount()),
    ticketCurrency: faker.finance.currencyCode(),
    flightNumber: faker.random.number(),
    seatAllocation: availableSeats,
    seatCapacity: availableSeats,
    ttl: Math.floor(flightArrival / 1000) //Delete flight after arrival
  };
  return flight;
}

function getRandomDate(start, end){
  start = start.getTime(), end = end.getTime();
  return new Date(start + Math.random() * (end - start));
}