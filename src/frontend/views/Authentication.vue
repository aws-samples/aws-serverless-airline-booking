<template>
  <div class="row">
    <amplify-authenticator
      class="authenticator__form"
      :authConfig="authConfig"
      data-test="authenticator"
    ></amplify-authenticator>
  </div>
</template>

<script>
// @ts-ignore
import { AmplifyEventBus } from "aws-amplify-vue";

/**
 * Authentication view authenticates a customer and redirects to desired page if successful
 * Non-authenticated users are redirected to this view via Route Guards
 */
export default {
  name: "Authentication",
  /**
   * @param {string} redirectTo - Sets Route one must go once authenticated
   */
  props: {
    redirectTo: String
  },
  mounted() {
    /**
     * At mount lifecycle hook, it listens for `authState` event, and when successfully signed-in it redirects to desired page
     */
    AmplifyEventBus.$on("authState", info => {
      if (info === "signedIn") {
        // return to where we came from
        this.$router.push({ name: this.redirectTo });
      }
    });
  },
  data() {
    return {
      authConfig: {
        signUpConfig: {
          defaultCountryCode: "44",
          signUpFields: [
            {
              label: "First name",
              key: "given_name",
              required: true,
              displayOrder: 0
            },
            {
              label: "Family name",
              key: "family_name",
              required: true,
              displayOrder: 1
            }
          ]
        }
      }
    };
  }
};
</script>

<style lang="stylus">
@import '~variables'

:root
  // Not a safe way to override as this can change at build
  // https://github.com/aws-amplify/amplify-js/issues/2471
  --amazonOrange $secondary !important
  --color-primary $primary !important

.authenticator__form
  @media only screen and (min-device-width: 700px)
    margin auto
    padding 15vmin

  > *
    font-family 'Raleway', 'Open Sans', sans-serif

  @media only screen and (min-device-width: 300px) and (max-device-width: 700px)
    > div
      min-width 80vw
      padding 10vmin
</style>
