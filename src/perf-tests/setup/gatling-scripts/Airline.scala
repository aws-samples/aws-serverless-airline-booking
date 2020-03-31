
import io.gatling.core.Predef._
import io.gatling.core.Predef.{constantUsersPerSec,atOnceUsers,_}
import io.gatling.http.Predef._
import scala.concurrent.duration._
import java.util.concurrent.ThreadLocalRandom
import scala.util.Random

class Airline extends Simulation {

val APPSYNC_URL = sys.env("APPSYNC_URL") 
val API_URL     = sys.env("API_URL") 
val COGNITO_URL = sys.env("COGNITO_URL") 
val TOKEN_CSV = sys.env("TOKEN_CSV")
val STRIPE_PUBLIC_KEY = sys.env("STRIPE_PUBLIC_KEY")
val USER_COUNT = sys.env("USER_COUNT").toInt
val DURATION = sys.env("DURATION").toInt
val YEAR = 2020
val DEPARTURE_CODE = "LGW"
val ARRIVAL_CODE = "MAD"


object Flight {
      val randomString = csv(TOKEN_CSV).circular

      val headerMaps = Map("Content-Type" -> "application/json; charset=UTF-8", 
                              "Accept" -> "application/json, text/plain, */*",
                              "Origin" -> COGNITO_URL,
                              "User-Agent" -> "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"                          
                            )

      val query = feed(randomString)
                      .exec( _.set("YEAR", YEAR))
                      .exec( _.set("DEPARTURE_CODE", DEPARTURE_CODE))
                      .exec( _.set("ARRIVAL_CODE", ARRIVAL_CODE))
                      .exec(http("Search Flights")
                      .post(APPSYNC_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(ElFileBody("queries/listFlights.json"))
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
                      .post(APPSYNC_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(ElFileBody("queries/getLoyalty.json"))
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
                      .post(APPSYNC_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(ElFileBody("queries/listBookings.json"))                 
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

      val randomString = csv(TOKEN_CSV).random

      val headerMaps = Map("Content-Type" -> "application/x-www-form-urlencoded", 
                              "Accept" -> "application/json",
                              "Origin" -> "https://js.stripe.com",
                              "User-Agent" -> "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"                          
                            ) 

      val randSelect: Random = new Random()
      val randNum: Int = randSelect.nextInt(50)         

      val booking =  feed(randomString)
                      .exec( _.set("YEAR", YEAR))
                      .exec( _.set("DEPARTURE_CODE", DEPARTURE_CODE))
                      .exec( _.set("ARRIVAL_CODE", ARRIVAL_CODE))
                      .exec(_.set("STRIPE_PUBLIC_KEY", STRIPE_PUBLIC_KEY))    
                      .exec(http("Search Rand Flights")
                      .post(APPSYNC_URL)
                      .headers(headerMaps)
                      .header("Authorization", "${token}" )
                      .body(ElFileBody("queries/listFlights.json"))
                      .asJson
                      .check(bodyString.saveAs("Query Flights"))
                      .check(jsonPath("$..id").find(randNum).saveAs("bookingId"))
                      .check(jsonPath("$..ticketPrice").find(randNum).saveAs("ticketPrice"))
                      .check(status.not(404), status.not(500)))
                      .exec(session => {
                        println(session)
                        session
                      })
                      .exec(http("Stripe tokenization")
                      .post("https://api.stripe.com/v1/tokens")
                      .headers(headerMaps)
                      .formParamMap(Map(
                        "card[name]" -> "John",
                        "card[address_zip]" -> "NC2+8234",
                        "card[address_country]" -> "UK",
                        "card[number]" -> "4242424242424242",
                        "card[cvc]" -> "123",
                        "card[exp_month]" -> "08",
                        "card[exp_year]" -> "32",
                        "guid" -> "7f94f22b-dd03-4d25-9482-48df472123dd",
                        "muid" -> "999143d3-02bc-4fc3-bf5f-510270268507",
                        "sid"  -> "5fa32dea-d7ca-4154-8efd-3181894f126f",
                        "key"  -> "${STRIPE_PUBLIC_KEY}"
                      ))
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
                      .body(ElFileBody("queries/processCharge.json"))
                      .asJson
                      .check(jsonPath("$.createdCharge.id").saveAs("chargeId")))
                      .exec(s => {
                        println(s)
                        s
                      })
                      .feed(randomString)
                      .exec(http("Process booking")
                      .post(APPSYNC_URL)
                      .header("Accept", "application/json, text/plain, */*")
                      .header("Content-Type", "application/json;charset=UTF-8")
                      .header("Authorization", "${token}")
                      .header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
                      .body(ElFileBody("queries/processBooking.json"))
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
    searchFlight.inject(
       constantUsersPerSec(USER_COUNT) during (DURATION) randomized),
    profile.inject(
      rampUsersPerSec(1) to USER_COUNT during (DURATION) randomized), 
    listUserBookings.inject(
      rampUsersPerSec(1) to USER_COUNT during (DURATION) randomized), 
    newBooking.inject(
      constantUsersPerSec(USER_COUNT) during (DURATION) randomized))
}
