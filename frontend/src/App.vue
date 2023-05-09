<template>
  <v-app>
    <Navbar />
    <v-main class="flex-grow-1" :class="{ 'is-full-screen': isFullScreen }"
      ><router-view
    /></v-main>
    <Footer v-if="!hideFooter" class="flex-grow-0" />
    <Notifications />
  </v-app>
</template>

<script setup lang="ts">
import Navbar from '@/components/base/Navbar.vue'
import Footer from '@/components/base/Footer.vue'
import Notifications from '@/components/base/Notifications.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const hideFooter = computed(() => {
  return route.meta.hideFooter
})

const isFullScreen = computed(() => {
  return route.meta.isFullScreen
})
</script>

<style scoped lang="scss">
.v-main.is-full-screen {
  height: 100vh;
}
</style>
