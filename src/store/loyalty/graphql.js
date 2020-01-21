export const fetchLoyaltyQuery = `query getLoyalty_status($cust_id: ID!) {
      getLoyalty_status(cust_id: $cust_id) {
        cust_id
        points
        tier
        remaining_pointss
      }
    }`
