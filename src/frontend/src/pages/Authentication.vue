<template>
  <div class="row">
    <amplify-authenticator
      v-if="authState !== 'signedin'"
      :form-fields.prop="formFields"
      username-alias="username"
      data-test="authenticator"
      validationErrors=""
    >
      <amplify-sign-up
        slot="sign-up"
        username-alias="username"
        :form-fields.prop="formFields"
      ></amplify-sign-up>
      <amplify-totp-setup slot="totp-setup"></amplify-totp-setup>
    </amplify-authenticator>

    <amplify-sign-out v-if="authState == 'signedin'"></amplify-sign-out>
  </div>
</template>

<script>
// @ts-ignore
import { onAuthUIStateChange, AuthState } from '@aws-amplify/ui-components'
import { Hub, Logger } from '@aws-amplify/core'

const logger = new Logger('Authentication')
const noAuthMessage = 'user is undefined'
const authMessageChannel = 'UI Auth'

/**
 * Authentication view authenticates a customer and redirects to desired page if successful
 * Non-authenticated users are redirected to this view via Route Guards
 */
export default {
  name: 'Authentication',
  /**
   * @param {string} redirectTo - Sets Route one must go once authenticated
   */
  props: {
    redirectTo: String
  },
  created() {
    onAuthUIStateChange((authState, authData) => {
      this.authState = authState
      this.user = authData

      if (authState === AuthState.SignIn) {
        logger.debug('Customer needs to sign in yet...')
      }

      if (authState === AuthState.SignedIn) {
        logger.debug('user successfully signed in!')
        logger.debug('user data: ', authData)
        this.$router.push({ name: this.redirectTo })
      }
    })

    Hub.listen(authMessageChannel, (data) => {
      const event = data.payload?.event ?? ''
      const message = data.payload?.message ?? ''

      // Ignore message if customer hasn't attempted to login yet
      if (message === noAuthMessage) return

      if (event === 'ToastAuthError') {
        this.$q.notify(message)
      }
    })
  },
  beforeDestroy() {
    return onAuthUIStateChange
  },
  data() {
    return {
      authState: undefined,
      user: undefined,
      formFields: [
        {
          type: 'given_name',
          label: 'First name',
          placeholder: 'First name',
          name: 'given_name',
          required: true
        },
        {
          type: 'family_name',
          label: 'Family name',
          placeholder: 'Last name',
          name: 'family_name',
          required: true
        },
        {
          type: 'username',
          name: 'username',
          label: 'Username',
          placeholder: 'demo',
          required: true
        },
        {
          type: 'password',
          required: true
        },
        {
          type: 'email',
          required: true
        }
      ]
    }
  }
}
</script>

<style lang="sass">
@import '../css/app'

amplify-authenticator
    @media only screen and (min-device-width: 700px)
        margin: 0 auto
        padding: 15vmin
        min-width: 100%
</style>
