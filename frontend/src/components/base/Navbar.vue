<template>
  <v-app-bar app class="base-navbar">
    <v-toolbar-items>
      <v-btn to="/">Home</v-btn>
      <v-btn to="/sites" v-if="access_token">My Sites</v-btn>
      <v-btn to="/browse">Browse Monitoring Sites</v-btn>
      <v-btn href="">Visualize Data</v-btn>
    </v-toolbar-items>
    <v-spacer></v-spacer>
    <v-toolbar-items class="toolbar-items">
      <v-btn href="/profile" v-if="access_token">Profile</v-btn>
      <v-btn v-if="access_token" class="btn--sub" @click.prevent="logout"
        >Logout</v-btn
      >
      <v-btn to="/Login" v-else class="btn--sub">Login/Sign Up</v-btn>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { computed } from 'vue'

const authStore = useAuthStore()
authStore.fetchAccessToken()

const access_token = computed(() => authStore.access_token)
const logout = authStore.logout
</script>

<style scoped lang="scss">
.toolbar-items {
  display: flex;
  justify-content: space-between;
}
</style>
