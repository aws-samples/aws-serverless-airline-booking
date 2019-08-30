const etlBucketName = process.env.ETL_BUCKET_NAME;
const AWS = require('aws-sdk');
const faker = require('faker');
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
  //Create 2 flights for the next 30 days
  console.log(allFlights);

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

  const outboundFlight = createFlight(airport1, airport2);
  const inboundFlight = createFlight(airport1, airport2);

  return [outboundFlight, inboundFlight];
}

function createFlight(departureAirport, arrivalAirport){
  const flight = {
    id: faker.random.uuid(),
    departureDate: new Date(),
    departureAirportCode: departureAirport.code,
    departureAirportName: departureAirport.name,
    departureCity: departureAirport.city,
    departureLocale: faker.random.locale,
    arrivalDate: new Date(),
    arrivalAirportCode: arrivalAirport.code,
    arrivalAirportName: arrivalAirport.name,
    arrivalCity: arrivalAirport.city,
    arrivalLocale: faker.random.locale(),
    ticketPrice: faker.finance.amount(),
    ticketCurrency: faker.finance.currencyCode(),
    flightNumber: (faker.hacker.abbreviation()+faker.random.number()),
    seatAllocation: (Math.floor(Math.random() * Math.floor(50))+1)+faker.random.arrayElement()
  };
  return flight;
}