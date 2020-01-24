import Flight from "../../shared/models/FlightClass"; // eslint-disable-line
import { Loading } from 'quasar';
import axios from 'axios';

const paymentEndpoint =
    process.env.VUE_APP_PaymentEndpoint || 'no payment gateway endpoint set';

/**
 *
 * Process Payment function - processPayment calls Payment endpoint to pre-authorize charge upon tokenized payment details
 *
 * @param {object} obj - Object containing params to process payment
 * @param {object} obj.paymentDetails - Payment details captured during flight selection
 * @param {string} obj.paymentDetails.name - Payment card holder's name
 * @param {string} obj.paymentDetails.address_country - Payment card registered country
 * @param {string} obj.paymentDetails.address_postcode - Payment card registered postcode
 * @param {object} obj.paymentDetails.card - Payment card details
 * @param {string} obj.paymentDetails.card.number - Payment card number
 * @param {string} obj.paymentDetails.card.expireMonth - Payment expireMonth e.g 1 (January)
 * @param {string} obj.paymentDetails.card.expireYear - Payment expireYear e.g 22 (2022)
 * @param {number} obj.paymentDetails.card.cvc - Payment cvc e.g (444)
 * @param {Flight} obj.outboundFlight - Outbound flight
 * @param {string} obj.customerEmail - Customer Email address for payment notification
 * @returns {promise} - Promise representing whether payment was successfully pre-authorized
 * @example
 *   let chargeToken = await processPayment({
 *      paymentDetails,
 *      outboundFlight,
 *      customerEmail
 *   });
 */
export async function processPayment ({
  paymentDetails,
  outboundFlight,
  customerEmail
}) {
  console.group('store/bookings/actions/payment/processPayment');
  Loading.show({
    message: 'Charging a pre-authorization...'
  });

  if (!paymentDetails) throw new Error('Invalid payment token');

  const chargeData = {
    name: paymentDetails.name,
    address_postcode: paymentDetails.address_postcode,
    address_country: paymentDetails.address_country,
    email: customerEmail,
    amount: outboundFlight.ticketPrice,
    currency: outboundFlight.ticketCurrency,
    description: `Dummy payment for flight number ${outboundFlight.flightNumber}`,
    card: {
      number: paymentDetails.card.number,
      expireMonth: paymentDetails.card.expireMonth,
      expireYear: paymentDetails.card.expireYear,
      cvc: paymentDetails.card.cvc
    }
  };

  console.log('Charge data to be processed');
  console.log(chargeData);

  try {
    const data = await axios.post(paymentEndpoint, chargeData);
    const {
      data: {
        createdCharge: { id: chargeId }
      }
    } = data;

    Loading.show({
      message: 'Payment authorized successfully...'
    });

    console.groupEnd();
    return chargeId;
  } catch (err) {
    const errorMessage = `Error when processing payment: ${err.message}`
    console.groupEnd()
    throw new Error(errorMessage)
  }
}
