
import io.gatling.core.Predef._
import io.gatling.core.Predef.{constantUsersPerSec,atOnceUsers,_}
import io.gatling.http.Predef._
import scala.concurrent.duration._
import java.util.concurrent.ThreadLocalRandom
import scala.util.Random

class setupUsers extends Simulation {

val COGNITO_URL = sys.env("COGNITO_URL")
val CLIENT_ID = sys.env("COGNITO_CLIENT_ID")

// Where we provide a CSV file with x username and password and the below will create those users in Cognito
object Create {

    val userAccountList = csv("user.csv").random

    val headerMaps = Map("Content-Type" -> "application/x-amz-json-1.1", 
                            "Accept" -> "*/*",
                            "Origin" ->  COGNITO_URL,
                            "X-Amz-Target" -> "AWSCognitoIdentityProviderService.SignUp",
                            "X-Amz-User-Agent" -> "aws-amplify/0.1.x js",
                            "Sec-Fetch-Mode" -> "cors",
                            "Sec-Fetch-Site" -> "cross-site",
                            "User-Agent" -> "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"                          
                          )

    val account = feed(userAccountList)
                    .exec( _.set("CLIENT_ID", CLIENT_ID) )
                    .exec(http("Create Account")
                    .post(COGNITO_URL)
                    .headers(headerMaps)
                    .body(StringBody("""{"ClientId":"${CLIENT_ID}","Username":"${username}","Password":"${password}","UserAttributes":[{"Name":"given_name","Value":"${given_name}"},{"Name":"family_name","Value":"${family_name}"},{"Name":"email","Value":"${email}"},{"Name":"phone_number","Value":"${phone_number}"}],"ValidationData":null}"""))
                    .check(bodyString.saveAs("CreateUserResponse"))
                    .check(status.not(404), status.not(500))
                    )
                    .exec(session => {
                       println(session)
                       session
                    })                    
      .pause(1)
  }

   val newUser = scenario("Create New Users").exec(Create.account)

    setUp(newUser.inject(constantConcurrentUsers(10) during (5 seconds)))
}
