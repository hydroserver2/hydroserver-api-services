<script>
import Navbar from "./components/Navbar.vue";
export default {
  name: 'App',
  components: {
    Navbar
  }
}
</script>

<template>
  <v-app>
  <header>
    <Navbar/>
  </header>
  <v-main>
    <router-view/>
  </v-main>
  </v-app>
</template>

<style scoped>
</style>
