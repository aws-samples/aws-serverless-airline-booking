<template>
  <div class="row">
    <div class="col-12 wrapper">
      <div class="heading">
        <div class="text-primary q-display-1 loyalty__heading--name">
          Heitor F. Lessa
        </div>
        <div class="loyalty__heading--tier">
          <div class="q-title loyalty__heading-tier-name">
            {{ loyalty.level }}
          </div>
          <div class="q-subtitle text-bold loyalty__heading-tier-number">
            {{ Number(loyalty.membershipNumber).toLocaleString("en") }}
          </div>
        </div>
      </div>
      <div class="wrapper">
        <div class="row loyalty__progress">
          <div class="col-7 loyalty__progress--points">
            <div class="q-display-1">
              {{ Number(loyalty.points).toLocaleString("en") }}
            </div>
            <div class="q-title text-primary text-bold">Points</div>
          </div>
          <div class="col-4 loyalty__progress--next-tier">
            <div class="q-display-1">{{ loyalty.percentage }}%</div>
            <div class="q-title text-primary text-bold">Next Tier Progress</div>
            <q-progress :percentage="loyalty.percentage" color="secondary" />
          </div>
        </div>
        <div class="row">
          <div class="profile__preferences--heading col-12 text-left q-mt-lg">
            <q-toolbar color="grey-1 text-black">
              <q-toolbar-title class="text-bold">Preferences</q-toolbar-title>
            </q-toolbar>
          </div>
          <div class="profile__preferences-options col-12">
            <q-list highlight no-border class="q-pa-none q-ml-md" link>
              <a @click="choosePreference('diet')">
                <q-item class="q-pa-none q-mt-md profile__preferences-option">
                  <q-icon name="tune" size="2.6rem" />
                  <q-item-main
                    class="text-bold q-title q-ml-md"
                    label="Dietary requirements"
                  />
                </q-item>
              </a>
              <a @click="choosePreference('luggage')">
                <q-item class="q-pa-none q-mt-md profile__preferences-option">
                  <q-icon name="tune" size="2.6rem" />
                  <q-item-main
                    class="text-bold q-title q-ml-md"
                    label="Luggage"
                  />
                </q-item>
              </a>
            </q-list>
          </div>
        </div>
      </div>
      <amplify-sign-out class="Form--signout"></amplify-sign-out>
    </div>
  </div>
</template>

<script>
// @ts-nocheck
import { mapState, mapGetters } from "vuex";
import { AmplifyEventBus } from "aws-amplify-vue";

/**
 *
 * Profile view displays a current Loyalty progress and points, and allow customers to set preferences.
 */
export default {
  name: "Profile",
  /**
   * @param {object} user - Current authenticated user from Profile module
   * @param {boolean} isAuthenticated - Getter from Profile module
   * @param {Loyalty} loyalty - Loyalty data from Loyalty module
   */
  computed: {
    ...mapState({
      user: state => state.profile.user,
      loyalty: state => state.loyalty.loyalty
    }),
    ...mapGetters("profile", ["isAuthenticated"])
  },
  methods: {
    choosePreference(option) {
      const defaultDialogOpts = {
        cancel: true,
        preventClose: true,
        color: "secondary"
      };

      const luggageDialog = {
        title: "Luggage preference",
        message: "How many luggages would you like to check-in with?",
        options: {
          type: "radio",
          model: "opt2",
          items: [
            { label: "1", value: "1", color: "primary" },
            { label: "2", value: "2" },
            { label: "3", value: "3" }
          ]
        }
      };

      const dietaryDialog = {
        title: "Dietary preference",
        message: "What's your dietary requirement?",
        options: {
          type: "radio",
          model: "opt2",
          items: [
            { label: "Vegatarian", value: "vegetarian", color: "secondary" },
            { label: "Vegan", value: "vegan" },
            { label: "Dairy-free", value: "dairy-free" },
            { label: "Regular", value: "regular" }
          ]
        }
      };

      let dialog = {
        ...defaultDialogOpts,
        ...(option === "luggage" ? luggageDialog : dietaryDialog)
      };

      this.$q
        .dialog(dialog)
        .then(choice => this.$q.notify(`${option}: ${choice}`))
        .catch(() => "No option selected");
    }
  },
  async mounted() {
    /** Amplify clears out cookies and any storage that can map to users
     * However it is on us to clear out our own store and redirect to Auth
     * If customer decides to sign out we redirect it to home, and subsequentially to authentication
     */
    AmplifyEventBus.$on("authState", info => {
      if (info === "signedOut") {
        this.$store
          .dispatch("profile/getSession")
          .catch(
            this.$router.push({ name: "auth", query: { redirectTo: "home" } })
          );
      }
    });

    // authentication guards prevent authenticated users to view Profile
    // however, the component doesn't stop from rendering asynchronously
    // this guarantees we attempt talking to Loyalty service
    // if our authentication guards && profile module have an user in place
    if (this.isAuthenticated) {
      await this.$store.dispatch("loyalty/fetchLoyalty");
    }
  }
};
</script>

<style lang="stylus">
/**
 * Amplify authenticatior HOC as of now doesn't provide overriding mechanisms for UI
 * we use CSS Root variables along with an authentication-form injected class for consistent experience
 */
@import '~variables'

a
  text-decoration none
  color black

.loyalty__heading
  &--tier
    margin $between-content-margin

.loyalty__progress
  &--points > *
    margin $between-content-margin

  &--next-tier > *
    margin $between-content-margin

.profile__preferences-option
  &:hover
    cursor pointer

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
