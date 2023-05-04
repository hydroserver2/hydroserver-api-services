<template>
  <v-app-bar app density="compact" scroll-behavior="elevate">
    <template v-if="mdAndDown" v-slot:append>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
    </template>

    <router-link :to="{ path: `/` }" class="logo">
      <v-img class="mr-4" :src="appLogo" alt="HydroServer home" width="10rem" />
    </router-link>

    <template v-if="!mdAndDown">
      <v-btn
        v-for="path of paths"
        :key="path.attrs?.to || path.attrs?.href"
        v-bind="path.attrs"
        :id="`navbar-nav-${path.label.replaceAll(/[\/\s]/g, ``)}`"
        :elevation="0"
        :class="path.isActive && path.isActive() ? 'primary' : ''"
        class="ma-1"
        color="white"
        variant="flat"
      >
        {{ path.label }}
        <v-icon v-if="path.isExternal" small class="ml-2" right
          >mdi-open-in-new</v-icon
        >
      </v-btn>

      <v-spacer></v-spacer>

      <template v-if="authStore.isLoggedIn">
        <v-btn elevation="2" rounded>
          <v-icon>mdi-account-circle</v-icon>
          <v-icon>mdi-menu-down</v-icon>

          <v-menu bottom left activator="parent">
            <v-list class="pa-0">
              <v-list-item
                :to="{ path: '/profile' }"
                active-class="primary white--text"
              >
                <template v-slot:prepend
                  ><v-icon>mdi-account-circle</v-icon></template
                >

                <v-list-item-title>Account</v-list-item-title>
              </v-list-item>

              <v-divider></v-divider>

              <v-list-item id="navbar-logout" @click="authStore.logout">
                <template v-slot:prepend><v-icon>mdi-logout</v-icon></template>
                <v-list-item-title>Log Out</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-btn>
      </template>

      <template v-else>
        <v-btn prepend-icon="mdi-login" to="/Login">Login</v-btn>
        <v-btn prepend-icon="mdi-account-plus-outline" to="/SignUp"
          >Sign Up</v-btn
        >
      </template>
    </template>
  </v-app-bar>

  <v-navigation-drawer v-if="mdAndDown" temporary v-model="drawer">
    <v-list density="compact" nav>
      <v-list-item
        v-for="path of paths"
        v-bind="path.attrs"
        :prepend-icon="path.icon"
        :title="path.label"
        :value="path.attrs.to || path.attrs.href"
        :class="path.isActive && path.isActive() ? 'primary' : ''"
      ></v-list-item>
    </v-list>

    <v-divider></v-divider>

    <v-list density="compact" nav>
      <template v-if="authStore.isLoggedIn">
        <v-list-item to="/profile" prepend-icon="mdi-account-circle"
          >Profile</v-list-item
        >
        <v-list-item prepend-icon="mdi-logout" @click.prevent="authStore.logout"
          >Logout</v-list-item
        >
      </template>

      <template v-else>
        <v-list-item prepend-icon="mdi-login" to="/Login">Login</v-list-item>
        <v-list-item prepend-icon="mdi-account-plus-outline" to="/SignUp"
          >Sign Up</v-list-item
        >
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { ref } from 'vue'
import { useDisplay } from 'vuetify/lib/framework.mjs'
import appLogo from '@/assets/ciroh.png'

const authStore = useAuthStore()
const { mdAndDown } = useDisplay()
const drawer = ref(false)

authStore.fetchAccessToken()

const paths: {
  attrs: { to?: string; href?: string }
  label: string
  icon: string
  isExternal?: boolean
  isActive?: () => boolean
}[] = [
  {
    attrs: { to: '/' },
    label: 'Home',
    icon: 'mdi-home',
  },
  {
    attrs: { to: '/sites' },
    label: 'My Sites',
    icon: 'mdi-map-marker-multiple',
  },
  {
    attrs: { to: '/browse' },
    label: 'Browse Monitoring Sites',
    icon: 'mdi-layers-search',
  },
  {
    attrs: { to: '/sites' },
    label: 'Visualize Data',
    icon: 'mdi-chart-timeline-variant',
  },
]
</script>

<style scoped lang="scss"></style>
