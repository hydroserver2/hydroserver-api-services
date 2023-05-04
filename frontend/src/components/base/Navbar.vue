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
        active-class="primary"
        :class="path.isActive && path.isActive() ? 'primary' : ''"
      >
        {{ path.label }}
        <v-icon v-if="path.isExternal" small class="ml-2" right
          >mdi-open-in-new</v-icon
        >
      </v-btn>

      <!-- <v-btn to="/sites" v-if="access_token">My Sites</v-btn>
      <v-btn to="/browse">Browse Monitoring Sites</v-btn>
      <v-btn href="">Visualize Data</v-btn> -->

      <v-spacer></v-spacer>

      <v-btn href="/profile" v-if="access_token">Profile</v-btn>
      <v-btn v-if="access_token" @click.prevent="authStore.logout"
        >Logout</v-btn
      >

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
        prepend-icon="mdi-view-dashboard"
        :title="path.label"
        :value="path.attrs.to || path.attrs.href"
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { ref } from 'vue'
import { computed } from 'vue'
import { useDisplay } from 'vuetify/lib/framework.mjs'
import appLogo from '@/assets/ciroh.png'

const authStore = useAuthStore()
const { mdAndDown } = useDisplay()
const drawer = ref(false)

authStore.fetchAccessToken()
const access_token = computed(() => authStore.access_token)

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
    icon: 'mdi-bookmark-multiple',
  },
  {
    attrs: { to: '/sites' },
    label: 'My Sites',
    icon: 'mdi-bookmark-multiple',
  },
  {
    attrs: { to: '/browse' },
    label: 'Browse Monitoring Sites',
    icon: 'mdi-bookmark-multiple',
  },
  {
    attrs: { to: '/sites' },
    label: 'Visualize Data',
    icon: 'mdi-bookmark-multiple',
  },
]
</script>

<style scoped lang="scss"></style>
