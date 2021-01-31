export const getLoyalty = `query getLoyalty($customer: String) {
  getLoyalty(customer: $customer) {
    points
    level
    remainingPoints
  }
}
`
