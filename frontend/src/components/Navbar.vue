<template>
  <v-app-bar app>
    <v-toolbar-title>
      <router-link to="/" class="header__logo">
        <v-img src="" alt="Hydro Server Logo" />
      </router-link>
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-toolbar-items>
      <v-btn to="/sites" v-if="access_token">My Sites</v-btn>
      <v-btn href="">Browse Monitoring Sites</v-btn>
      <v-btn href="">Visualize Data</v-btn>
      <v-btn href="" v-if="access_token">Profile</v-btn>
      <v-btn v-if="access_token" class="btn--sub" @click.prevent="logout">Logout</v-btn>
      <v-btn to="/Login" v-else class="btn--sub">Login/Sign Up</v-btn>
    </v-toolbar-items>
  </v-app-bar>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Navbar',
  computed: {
    ...mapState(['loggingIn', 'loginError', 'access_token'])
  },
  created() { this.fetchAccessToken() },
  methods: {
    ...mapActions(['login', 'logout', "fetchAccessToken"]),
  },
};
</script>

<style scoped>
.btn--sub {
  background-color: #2980b9;
}
</style>