<template>
  <v-app-bar app density="compact" elevation="2">
    <template v-if="mdAndDown" v-slot:append>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
    </template>

    <router-link :to="{ path: `/` }" class="logo">
      <v-img
        class="mr-4"
        :src="appLogo"
        alt="HydroServer home"
        width="7.5rem"
      />
    </router-link>

    <template v-if="!mdAndDown">
      <div v-for="path of paths" :key="path.name">
        <v-btn
          v-if="!path.menu"
          v-bind="path.attrs"
          :id="`navbar-nav-${path.label.replaceAll(/[\/\s]/g, ``)}`"
          :elevation="0"
          :class="path.isActive && path.isActive() ? 'primary' : ''"
          class="ma-1"
          color="surface"
          variant="flat"
        >
          {{ path.label }}
        </v-btn>
        <v-menu
          v-else
          :id="`navbar-nav-${path.label.replaceAll(/[\/\s]/g, ``)}`"
        >
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              :elevation="0"
              class="ma-1"
              color="surface"
              variant="flat"
            >
              {{ path.label }}
            </v-btn>
          </template>
          <v-list>
            <v-list-item v-for="menuItem of path.menu" v-bind="menuItem.attrs">
              <v-list-item-title>
                {{ menuItem.label }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
      <v-spacer></v-spacer>

      <template v-if="authStore.isLoggedIn">
        <v-btn elevation="2" rounded class="account-logout-button">
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
        <v-btn
          class="navbar-login-button"
          prepend-icon="mdi-login"
          to="/Login"
          color="surface"
          variant="flat"
          >Log In</v-btn
        >
        <v-btn
          class="signup-btn"
          prepend-icon="mdi-account-plus-outline"
          to="/SignUp"
          color="surface"
          variant="flat"
          >Sign Up</v-btn
        >
      </template>
    </template>
  </v-app-bar>

  <v-navigation-drawer
    v-if="mdAndDown"
    temporary
    v-model="drawer"
    location="right"
  >
    <v-list density="compact" nav>
      <div v-for="path of paths">
        <v-list-item
          v-if="path.attrs"
          v-bind="path.attrs"
          :title="path.label"
          :prepend-icon="path.icon"
          :value="path.attrs.to || path.attrs.href"
          :class="path.isActive && path.isActive() ? 'primary' : ''"
        ></v-list-item>
        <div v-else>
          <v-list-item
            v-for="menuItem of path.menu"
            v-bind="menuItem.attrs"
            :title="menuItem.label"
            :prepend-icon="menuItem.icon"
            :value="menuItem.attrs.to || menuItem.attrs.href"
            :class="menuItem.isActive && menuItem.isActive() ? 'primary' : ''"
          ></v-list-item>
        </div>
      </div>
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
import appLogo from '@/assets/hydroserver-icon-min.png'

const authStore = useAuthStore()
const { mdAndDown } = useDisplay()
const drawer = ref(false)

const paths: {
  name: string
  attrs?: { to?: string; href?: string }
  label: string
  icon?: string
  menu?: any[]
  isExternal?: boolean
  isActive?: () => boolean
}[] = [
  {
    name: 'home',
    attrs: { to: '/' },
    label: 'Home',
    icon: 'mdi-home',
  },
  {
    name: 'browse',
    attrs: { to: '/browse' },
    label: 'Browse Monitoring Sites',
    icon: 'mdi-layers-search',
  },
  {
    name: 'management',
    label: 'Data Management',
    menu: [
      {
        attrs: { to: '/sites' },
        label: 'My Sites',
        icon: 'mdi-map-marker-multiple',
      },
      {
        attrs: { to: '/Metadata' },
        label: 'Manage Metadata',
        icon: 'mdi-database-cog',
      },
      {
        attrs: { to: '/data-sources' },
        label: 'Manage Data Sources',
        icon: 'mdi-file-chart',
      },
      {
        attrs: { to: '/data-loaders' },
        label: 'Manage Data Loaders',
        icon: 'mdi-file-upload',
      },
    ],
  },
  {
    name: 'docs',
    attrs: { href: 'https://hydroserver2.github.io/docs/' },
    label: 'Docs',
    icon: 'mdi-file-document',
  },
  {
    name: 'contact us',
    attrs: { to: '/contact' },
    label: 'Contact Us',
    icon: 'mdi-email',
  },
  // {
  //   attrs: { to: '/sites' },
  //   label: 'Visualize Data',
  //   icon: 'mdi-chart-timeline-variant',
  // },
]
</script>

<style scoped lang="scss"></style>
