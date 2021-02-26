<template>
  <div class="row q-pt-lg">
    <div class="col-12 wrapper">
      <div class="heading">
        <div
          class="text-primary text-h4 loyalty__heading--name"
          data-test="loyalty-name"
        >
          {{ fullName }}
        </div>
        <div class="loyalty__heading--tier">
          <div
            class="text-h6 loyalty__heading-tier-name"
            data-test="loyalty-level"
          >
            {{ loyalty.level || 'bronze' }}
          </div>
        </div>
      </div>
      <div class="wrapper">
        <div class="row loyalty__progress">
          <div class="col-6 loyalty__progress--points">
            <div class="text-h4 loyalty__points" data-test="loyalty-points">
              {{ loyalty.points || 0 }}
            </div>
            <div class="text-h6 text-primary text-bold">Points</div>
          </div>
          <div class="col-6 loyalty__progress--next-tier">
            <div class="text-h4" data-test="loyalty-next-tier">
              {{ loyalty.percentage || 0 }}%
            </div>
            <div class="text-h6 text-primary text-bold q-mt-xs">
              Tier Progress
            </div>
            <q-linear-progress
              size="1vh"
              :value="progressPercentage"
              color="secondary"
            />
          </div>
        </div>

        <div class="row q-pt-xl">
          <amplify-sign-out data-test="authenticator"></amplify-sign-out>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// @ts-nocheck
import { mapState, mapGetters } from 'vuex'
import { onAuthUIStateChange, AuthState } from '@aws-amplify/ui-components'
import { Logger } from '@aws-amplify/core'

const logger = new Logger('Profile')

/**
 *
 * Profile view displays a current Loyalty progress and points, and allow customers to set preferences.
 */
export default {
  name: 'Profile',
  /**
   * @param {object} user - Current authenticated user from Profile module
   * @param {boolean} isAuthenticated - Getter from Profile module
   * @param {Loyalty} loyalty - Loyalty data from Loyalty module
   */
  computed: {
    ...mapState({
      user: (state) => state.profile.user,
      loyalty: (state) => state.loyalty.loyalty
    }),
    ...mapGetters({
      isAuthenticated: 'profile/isAuthenticated',
      firstName: 'profile/firstName',
      lastName: 'profile/lastName'
    }),
    fullName() {
      return `${this.firstName} ${this.lastName}`
    },
    progressPercentage() {
      return this.loyalty.percentage / 100 || 0
    }
  },
  async mounted() {
    // Amplify clears out cookies and any storage that can map to users
    // However it is on us to clear out our own store and redirect to Auth
    // If customer decides to sign out we redirect it to home, and subsequentially to authentication

    onAuthUIStateChange((authState, authData) => {
      if (authState === AuthState.SignedOut) {
        this.$store
          .dispatch('profile/getSession')
          .catch(
            this.$router.push({ name: 'auth', query: { redirectTo: 'home' } })
          )
      }
    })

    // authentication guards prevent authenticated users to view Profile
    // however, the component doesn't stop from rendering asynchronously
    // this guarantees we attempt talking to Loyalty service
    // if our authentication guards && profile module have an user in place
    try {
      if (this.isAuthenticated) {
        await this.$store.dispatch('loyalty/fetchLoyalty')
      }
    } catch (error) {
      logger.error('Error while fetching loyalty data: ', error)
      this.$q.notify(
        `Error while fetching Loyalty - Check browser console messages`
      )
    }
  }
}
</script>

<style lang="sass">
@import '../css/app'

a
  text-decoration: none
  color: black

.loyalty__heading
  &--tier
    margin: $between-content-margin

.loyalty__progress
  &--points > *
    margin: $between-content-margin

  &--next-tier
    margin: $between-content-margin

.q-linear-progress
  width: 90% !important

amplify-sign-out
    padding: 0vmin 2vmin
    width: 100%
    margin-top: 10vh
</style>
