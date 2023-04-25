<script>
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
export default {
  name: 'App',
  components: {
    Footer,
    Navbar
  }
}
</script>

<template>
  <v-app class="main-layout">
    <Navbar/>
    <v-main class="main-content"><router-view/></v-main>
    <Footer/>
  </v-app>
</template>

<style>
.main-layout {
  display: flex;
  flex-direction: column;
}

.main-content {
  min-height: 100vh;
}
</style>
