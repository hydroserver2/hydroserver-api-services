<template>
  <v-app>
    <Navbar />
    <v-main><router-view /></v-main>
    <Footer />
  </v-app>
</template>

<script lang="ts">
import Navbar from '@/components/base/Navbar.vue'
import Footer from '@/components/base/Footer.vue'
export default {
  name: 'App',
  components: {
    Footer,
    Navbar,
  },
}
</script>

<style scoped lang="scss"></style>
