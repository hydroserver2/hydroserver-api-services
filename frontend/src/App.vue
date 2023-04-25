<template>
  <v-app class="main-layout">
    <Navbar />
    <v-main class="main-content"><router-view /></v-main>
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

<style scoped lang="scss">
.main-layout {
  display: flex;
  flex-direction: column;
}

.main-content {
  min-height: 100vh;
}
</style>
