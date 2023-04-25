<template>
  <v-app>
    <header>
      <Navbar />
    </header>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Navbar from '@/components/base/Navbar.vue'
export default {
  name: 'App',
  components: {
    Navbar,
  },
}
</script>

<style scoped lang="scss"></style>
