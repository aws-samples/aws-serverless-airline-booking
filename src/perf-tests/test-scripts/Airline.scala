
import io.gatling.core.Predef._
import io.gatling.core.Predef.{constantUsersPerSec,atOnceUsers,_}
import io.gatling.http.Predef._
import scala.concurrent.duration._
import java.util.concurrent.ThreadLocalRandom
import scala.util.Random

class Airline extends Simulation {

val GRAPHQL_URL = sys.env("GRAPHQL_URL") 
val API_URL     = sys.env("API_URL") 
val COGNITO_URL = sys.env("COGNITO_URL") 
val TOKEN_CSV = sys.env("TOKEN_CSV")

object Flight {
      val randomString = csv(TOKEN_CSV).circular

      val headerMaps = Map("Content-Type" -> "application/json; charset=UTF-8", 
                              "Accept" -> "application/json, text/plain, */*",
                              "Origin" -> COGNITO_URL,
                              "User-Agent" -> "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"                          
                            )

      val query = feed(randomString)    
                      .exec(http("Search Flights")
                      .post(GRAPHQL_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(StringBody("""{"query":"query ListFlights($filter: ModelFlightFilterInput, $limit: Int, $nextToken: String) {  listFlights(filter: $filter, limit: $limit, nextToken: $nextToken) { items { id      departureDate      departureAirportCode      departureAirportName      departureCity      departureLocale      arrivalDate      arrivalAirportCode      arrivalAirportName      arrivalCity      arrivalLocale      ticketPrice      ticketCurrency      flightNumber      seatAllocation    }    nextToken  }}","variables":{"limit":50,"filter":{"departureDate":{"beginsWith":"2019"},"departureAirportCode":{"eq":"LGW"},"arrivalAirportCode":{"eq":"MAD"}}}}"""))
                      .asJson
                      .check(bodyString.saveAs("Query Flights"))
                      .check(status.not(404), status.not(500)))
                      .exec(session => {
                        println(session)
                        session
                      })                    
        .pause(1)
  }

object User {

      val randomString = csv("user-with-token.csv").random

      val headerMaps = Map("Content-Type" -> "application/json; charset=UTF-8", 
                              "Accept" -> "application/json, text/plain, */*",
                              "Origin" -> "https://develop.d3p67q4romop9c.amplifyapp.com",
                              "User-Agent" -> "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"                          
                            )

      val profile = feed(randomString)    
                      .exec(http("Retrieve Profile")
                      .post(GRAPHQL_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(StringBody("""{"query":"query getLoyalty($customer: String) {  getLoyalty(customer: $customer) {    points    level    remainingPoints  }}","variables":{}}"""))
                      .asJson
                      .check(bodyString.saveAs("User Profile"))
                      .check(status.not(404), status.not(500)))
                      .exec(session => {
                        println(session)
                        session
                      })                    
        .pause(1)

      val bookings = feed(randomString)    
                      .exec(http("List bookings")
                      .post(GRAPHQL_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(StringBody("""{"query":"query ListBookings($filter: ModelBookingFilterInput, $limit: Int, $nextToken: String) {  listBookings(filter: $filter, limit: $limit, nextToken: $nextToken) {    items {      id      status      bookingReference      outboundFlight {        id        departureDate        departureAirportCode        departureAirportName        departureCity        departureLocale        arrivalDate        arrivalAirportCode        arrivalAirportName        arrivalCity        arrivalLocale        ticketPrice        ticketCurrency        flightNumber      }      checkedIn      createdAt    }    nextToken  }}","variables":{}}"""))
                      .asJson
                      .check(bodyString.saveAs("Retrieve bookings"))
                      .check(status.not(404), status.not(500)))
                      .exec(session => {
                        println(session)
                        session
                      })                    
        .pause(1)
  }

object Make {

      val randomString = csv(TOKEN_CSV).circular

      val headerMaps = Map("Content-Type" -> "application/x-www-form-urlencoded", 
                              "Accept" -> "application/json",
                              "Origin" -> "https://js.stripe.com",
                              "User-Agent" -> "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"                          
                            )                 

      val booking =  feed(randomString)    
                      .exec(http("Search Rand Flights")
                      .post(GRAPHQL_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                     .body(StringBody("""{"query":"query ListFlights($filter: ModelFlightFilterInput, $limit: Int, $nextToken: String) {  listFlights(filter: $filter, limit: $limit, nextToken: $nextToken) { items { id      departureDate      departureAirportCode      departureAirportName      departureCity      departureLocale      arrivalDate      arrivalAirportCode      arrivalAirportName      arrivalCity      arrivalLocale      ticketPrice      ticketCurrency      flightNumber      seatAllocation    }    nextToken  }}","variables":{"limit":50, "filter":{"departureDate":{"beginsWith":"2019"},"departureAirportCode":{"eq":"LGW"},"arrivalAirportCode":{"eq":"MAD"}}}}"""))
                      .asJson
                      .check(bodyString.saveAs("Query Flights"))
                      .check(jsonPath("$..id").find(0).saveAs("bookingId"))
                      .check(jsonPath("$..ticketPrice").find(0).saveAs("ticketPrice"))
                      .check(status.not(404), status.not(500)))
                      .exec(session => {
                        println(session)
                        session
                      })
                      .exec(http("Stripe tokenization")
                      .post("https://api.stripe.com/v1/tokens")
                      .headers(headerMaps)
                      .formParam("card[name]","Pawan")
                      .formParam("card[address_zip]","HA2+8PXY")
                      .formParam("card[address_country]", "UK")
                      .formParam("card[number]", "4242424242424242")
                      .formParam("card[cvc]","123")
                      .formParam("card[exp_month]","08")
                      .formParam("card[exp_year]","25")
                      .formParam("guid","7f94f22b-dd03-4d25-9482-48df472123dd")
                      .formParam("muid","999143d3-02bc-4fc3-bf5f-510270268507")
                      .formParam("sid","5fa32dea-d7ca-4154-8efd-3181894f126f")    
                      .formParam("payment_user_agent","stripe.js%2F87a13246%3B+stripe-js-v3%2F87a13246") 
                      .formParam("key","pk_test_BpxANYCOZO7waMV3TrPQHjXa")                   
                      .check(status.not(404), status.not(500))
                      .check(jsonPath("$.id").saveAs("stripeToken")))
                      .exec(session => {
                        println(session)
                        session
                      })
                      .exec(http("Charge API")
                      .post(API_URL)
                      .header("Accept", "application/json, text/plain, */*")
                      .header("Content-Type", "application/json;charset=UTF-8")
                      .header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
                      .body(StringBody("""{"amount":${ticketPrice},"currency":"EUR","stripeToken":"${stripeToken}","description":"Payment by askdjas.adas@gmail.com","email":"askdjas.adas@gmail.com"}"""))
                      .asJson
                      .check(jsonPath("$.createdCharge.id").saveAs("chargeId")))
                      .exec(s => {
                        println(s)
                        s
                      })
                      .feed(randomString)
                      .exec(http("Process booking")
                      .post(GRAPHQL_URL)
                      .header("Accept", "application/json, text/plain, */*")
                      .header("Content-Type", "application/json;charset=UTF-8")
                      .header("Authorization", "${token}")
                      .header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
                      .body(StringBody("""{"query":"mutation ProcessBooking($input: CreateBookingInput!) {  processBooking(input: $input) {    id  }}","variables":{"input":{"paymentToken":"${chargeId}","bookingOutboundFlightId":"${bookingId}"}}}"""))
                      .asJson)
                      .exec(p => {
                        println(p)
                        p
                      })                                         
        .pause(1)
  }

  val searchFlight = scenario("Search Flights").exec(Flight.query)
  val profile = scenario("Retrieve User Profile").exec(User.profile)
  val listUserBookings = scenario("List User Bookings").exec(User.bookings)
  val newBooking = scenario("New Booking").exec(Make.booking)

setUp(
  // //  newUser.inject(constantConcurrentUsers(10) during (1 seconds)))
 
    searchFlight.inject(
       constantUsersPerSec(20) during (5 minutes) randomized),
    profile.inject(
      rampUsersPerSec(1) to 20 during (5 minutes) randomized), 
    listUserBookings.inject(
      rampUsersPerSec(1) to 20 during (5 minutes) randomized), 
    newBooking.inject(
      constantUsersPerSec(20) during (5 minutes) randomized))

  //   searchFlight.inject(
  //       rampUsersPerSec(0) to 10 during (5 minutes)),
  //   profile.inject(
  //     rampUsersPerSec(0) to 10 during (5 minutes)),
  //   listUserBookings.inject(
  //     rampUsersPerSec(0) to 10 during (5 minutes)),
  //   newBooking.inject(
  //     rampUsersPerSec(0) to 6 during (5 minutes))
  // ).throttle(
  //         reachRps(20) in (120 seconds),
  //         holdFor(1 minute),
  //         jumpToRps(10),
  //         holdFor(1 minute))

}
