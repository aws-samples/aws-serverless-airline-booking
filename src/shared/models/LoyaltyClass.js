/** Class representing Loyalty. All permutations of data from Loyalty, a different date format for instance, should happen here. */
export default class Loyalty {
  /**
   * Creates an instance of Loyalty.
   * @param {Object} Loyalty
   * @param {string} Loyalty.level - Loyalty Tier Level
   * @param {number} Loyalty.points - Sum of Loyalty points accumulated
   * @param {number} Loyalty.remainingPoints - Remaining Loyalty points to reach next tier level
   * @param {number} Loyalty.membershipNumber - Loyalty Membership Number
   * @example
   * let loyalty = new Loyalty({
   *    level: "purple",
   *    points: 324567,
   *    remainingPoints: 32456,
   *    membershipNumber: 32456,
   *    customer: "3fe22b2c-2b52-4a75-9db7-6cfc36a0cfcd"
   * })
   */
  constructor({ level, points, remainingPoints, membershipNumber }) {
    this.level = level;
    this.points = points;
    this.remainingPoints = remainingPoints;
    this.membershipNumber = membershipNumber;

    this.percentage = Math.ceil(
      (points / (points + remainingPoints)) * 100,
      // @ts-ignore
      1
    );
  }
}
