<template>
  <v-app-bar app class="base-navbar">
    <!--    <v-toolbar-title>-->
    <!--      <router-link to="/" class="header__logo">-->
    <!--        <v-img src="" alt="Hydro Server Logo" />CIROH HIS-->
    <!--      </router-link>-->
    <!--    </v-toolbar-title>-->

    <v-container>
      <v-btn variant="text" to="/">Home</v-btn>
      <v-btn variant="text" to="/sites" v-if="access_token">My Sites</v-btn>
      <v-btn variant="text" to="/browse">Browse Monitoring Sites</v-btn>
      <v-btn variant="text" href="">Visualize Data</v-btn>
    </v-container>

    <v-spacer></v-spacer>
    <v-btn variant="text" href="" v-if="access_token">Profile</v-btn>
    <v-btn variant="text" v-if="access_token" @click.prevent="logout"
      >Logout</v-btn
    >
    <v-btn v-else variant="text" to="/Login">Login/Sign Up</v-btn>
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
.toolbar-items {
  display: flex;
  justify-content: space-between;
}
</style>
