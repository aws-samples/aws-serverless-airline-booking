export const processBooking = `mutation ProcessBooking($input: CreateBookingInput!) {
  processBooking(input: $input) {
    id
  }
}
`;
