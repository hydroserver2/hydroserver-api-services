<template>
  <v-app-bar app>
    <v-toolbar-title>
      <router-link to="/" class="header__logo">
        <v-img src="" alt="Hydro Server Logo" />CIROH HIS
      </router-link>
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-toolbar-items>
      <v-btn to="/sites" v-if="access_token">My Sites</v-btn>
      <v-btn to="/browse">Browse Monitoring Sites</v-btn>
      <v-btn href="">Visualize Data</v-btn>
      <v-btn href="" v-if="access_token">Profile</v-btn>
      <v-btn v-if="access_token" class="btn--sub" @click.prevent="logout"
        >Logout</v-btn
      >
      <v-btn to="/Login" v-else class="btn--sub">Login/Sign Up</v-btn>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script lang="ts">
import { useAuthStore } from '@/store/authentication'
import { computed } from 'vue'

export default {
  name: 'Navbar',
  setup() {
    const authStore = useAuthStore()

    authStore.fetchAccessToken()

    const access_token = computed(() => authStore.access_token)
    const logout = authStore.logout

    return { access_token, logout }
  },
}
</script>

<style scoped lang="scss">
.btn--sub {
  background-color: #2980b9;
}
</style>
