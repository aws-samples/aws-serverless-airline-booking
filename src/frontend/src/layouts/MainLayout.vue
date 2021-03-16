<template>
  <q-layout view="hHh lpR fFf" class="bg-grey-1">
    <q-header>
      <q-toolbar class="text-center">
        <q-btn
          flat
          dense
          round
          @click="leftDrawerOpen = !leftDrawerOpen"
          aria-label="Menu"
        >
          <q-icon name="menu" />
        </q-btn>

        <q-toolbar-title class="brand">Flight App</q-toolbar-title>
        <q-btn
          flat
          round
          dense
          size="lg"
          icon="search"
          :to="{ name: 'home' }"
        />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      content-class="bg-grey-1"
      elevated
      @click.capture="drawerClick"
    >
      <q-list no-border link inset-delimiter>
        <q-item-label header class="text-grey-8"> Menu </q-item-label>
        <q-item :to="{ name: 'home' }" exact>
          <q-item-section avatar>
            <q-icon name="home" class="menu__icons--branded" />
          </q-item-section>
          <q-item-section class="text-dark">Home</q-item-section>
        </q-item>
        <q-item :to="{ name: 'profile' }" exact>
          <q-item-section avatar>
            <q-icon name="person" class="menu__icons--branded" />
          </q-item-section>
          <q-item-section class="text-dark">Profile</q-item-section>
        </q-item>
        <q-item :to="{ name: 'bookings' }" exact>
          <q-item-section avatar>
            <q-icon name="flight" class="menu__icons--branded" />
          </q-item-section>
          <q-item-section class="text-dark">My Bookings</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container class="content">
      <transition enter-active-class="animated fadeIn" appear>
        <router-view />
      </transition>
    </q-page-container>
  </q-layout>
</template>

<script>
export default {
  name: 'DefaultLayout',
  data() {
    return {
      leftDrawerOpen: false
    }
  },
  methods: {
    // Hides drawer after customer clicks on menu item
    drawerClick(e) {
      this.leftDrawerOpen = !this.leftDrawerOpen
      e.stopPropagation()
    }
  }
}
</script>

<style lang="sass" scoped>
.menu__icons--branded
  font-size: 43px !important
  color: $primary

.content
  padding-left: 0 !important
  max-width: 978px
  margin: 0 auto
</style>
