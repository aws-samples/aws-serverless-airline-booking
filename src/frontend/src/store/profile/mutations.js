/**
 *
 * Profile [Vuex Module Mutation](https://vuex.vuejs.org/guide/mutations.html) - SET_USER mutates Profile user state with given username as payload.
 *
 * When no username is given as a payload it sets to null.
 * @param {object} state - Vuex Profile Module State
 * @param {object} username - Payload to bet set as username ([CognitoUser interface](https://github.com/amazon-archives/amazon-cognito-identity-js/blob/6b87f1a30a998072b4d98facb49dcaf8780d15b0/lib/CognitoUser.js))
 * @param {string} username.username - CognitoUser username
 * @param {object} username.pool - CognitoUser User Pool information
 * @param {string} username.pool.userPoolId - CognitoUser User Pool information
 * @param {string} username.pool.clientId - CognitoUser User Pool information
 * @param {object} username.pool.client - CognitoUserClient
 * @param {string} username.pool.client.endpoint - CognitoUserClient endpoint information
 * @param {string} username.pool.client.userAgent - CognitoUserClient information user agent (e.g aws-amplify/0.1.x js)
 * @param {boolean} username.pool.advancedSecurityDataCollectionFlag - Whether Advanced Security Data collection is enabled
 * @param {string} username.pool.storage - CognitoUser User Pool information
 * @param {string} username.Session - CognitoUserSession
 * @param {object} username.client - CognitoUserClient
 * @param {string} username.client.endpoint - CognitoUserClient endpoint information
 * @param {string} username.client.userAgent - CognitoUserClient information user agent (e.g aws-amplify/0.1.x js)
 * @param {object} username.signInUserSession - CognitoUserSession
 * @param {object} username.signInUserSession.idToken - CognitoUserSession Identity Token info
 * @param {string} username.signInUserSession.idToken.jwtToken - CognitoUserSession Identity Token
 * @param {object} username.signInUserSession.idToken.payload - CognitoUserSession Identity JWT Payload info
 * @param {object} username.signInUserSession.refreshToken - CognitoUserSession Refresh Token info
 * @param {string} username.signInUserSession.refreshToken.jwtToken - CognitoUserSession Refresh Token
 * @param {object} username.signInUserSession.refreshToken.payload - CognitoUserSession Refresh JWT Payload info
 * @param {object} username.signInUserSession.accessToken - CognitoUserSession Access Token info
 * @param {string} username.signInUserSession.accessToken.jwtToken - CognitoUserSession Access Token
 * @param {object} username.signInUserSession.accessToken.payload - CognitoUserSession Access JWT Payload info
 * @param {number} username.signInUserSession.clockDrift - CognitoUserSession Clock Drift
 * @param {string} username.authenticationFlowType - CognitoUser authentication flow type (e.g USER_SRP_AUTH)
 * @param {string} username.storage - CognitoUser
 * @param {string} username.keyPrefix - CognitoUser
 * @param {string} username.userDataKey - CognitoUser
 * @param {object} username.attributes - CognitoUser attributes
 * @param {string} username.preferredMFA - CognitoUser
 * @see {@link getSession} for more info on action that calls SET_USER
 */
export const SET_USER = (state, username) => {
  state.user = username
}
