import Flight from "../../shared/models/FlightClass"; // eslint-disable-line
import { Loading } from "quasar";
import axios from "axios";

const paymentEndpoint =
  process.env.VUE_APP_PaymentChargeUrl || "no payment gateway endpoint set";

/**
 *
 * Process Payment function - processPayment calls Payment endpoint to pre-authorize charge upon tokenized payment details
 *
 * @param {object} obj - Object containing params to process payment
 * @param {object} obj.paymentToken - Tokenized payment info
 * @param {object} obj.paymentToken.details - Tokenized payment details including last4, id, etc.
 * @param {object} obj.paymentToken.id - Payment token
 * @param {Flight} obj.outboundFlight - Outbound flight
 * @param {string} obj.customerEmail - Customer Email address for payment notification
 * @returns {promise} - Promise representing whether payment was successfully pre-authorized
 * @example
 *   let chargeToken = await processPayment({
 *      paymentToken,
 *      outboundFlight,
 *      customerEmail
 *   });
 */
export async function processPayment({
  paymentToken,
  outboundFlight,
  customerEmail
}) {
  console.group("store/bookings/actions/processPayment");
  Loading.show({
    message: "Charging a pre-authorization..."
  });

  if (!paymentToken) throw "Invalid payment token";

  const chargeData = {
    amount: outboundFlight.ticketPrice,
    currency: outboundFlight.ticketCurrency,
    stripeToken: paymentToken.details.id,
    description: `Payment by ${customerEmail}`,
    email: customerEmail
  };

  console.log("Charge data to be processed");
  console.log(chargeData);
  try {
    const data = await axios.post(paymentEndpoint, chargeData);
    const {
      data: {
        createdCharge: { id: chargeId }
      }
    } = data;

    Loading.show({
      message: "Payment authorized successfully..."
    });

    console.groupEnd();
    return chargeId;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
