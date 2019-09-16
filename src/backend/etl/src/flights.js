const etlBucketName = process.env.ETL_BUCKET_NAME;
const AWS = require('aws-sdk');
const faker = require('faker');
const moment = require('moment');
const s3 = new AWS.S3();

let response;

exports.generate = async (event, context) => {
  console.log(event);

  const execution = event.execution;
  const index = event.index;
  const response = await s3.getObject({
    Bucket: etlBucketName,
    Key: event.routeFileKey
  }).promise();

  let routes = JSON.parse(response.Body.toString('utf-8'));
  console.log(routes.length);

  //for each route
  const allFlights = routes.map(route => generateFlights(route))
                           .reduce((acc, x) => acc.concat(x), []);

   console.log("all Flights ", allFlights.length);
  //write the file
  const chunkFilename = `raw/${execution}/flights/${index}_flights.json`
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
  }).reduce((arr, x) => arr.concat(x), []);

  return next30Days;
}

function createFlight(departureAirport, arrivalAirport, start, end){
  const flightDeparture = getRandomDate(start, end);
  const flightArrival = getRandomDate(flightDeparture, end);
  const flightNumber = (faker.hacker.abbreviation()+faker.random.number());
  const flight = {
    id: faker.random.uuid(),
    departureDate: flightDeparture,
    departureAirportCode: departureAirport.code,
    departureAirportName: departureAirport.name,
    departureCity: departureAirport.city,
    departureLocale: faker.random.locale,
    arrivalDate: flightArrival,
    arrivalAirportCode: arrivalAirport.code,
    arrivalAirportName: arrivalAirport.name,
    arrivalCity: arrivalAirport.city,
    arrivalLocale: faker.random.locale(),
    ticketPrice: faker.finance.amount(),
    ticketCurrency: faker.finance.currencyCode(),
    flightNumber: flightNumber.length > 4 ? flightNumber.substring(0, 4) : flightNumber,
    seatAllocation: (Math.floor(Math.random() * Math.floor(50))+1)
  };
  return flight;
}

function getRandomDate(start, end){
  start = start.getTime(), end = end.getTime();
  return new Date(start + Math.random() * (end - start));
}