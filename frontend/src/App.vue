<template>
  <v-app>
    <Navbar />
    <v-main class="flex-grow-1"><router-view /></v-main>
    <Footer class="flex-grow-0" />
    <Notifications />
  </v-app>
</template>

<script lang="ts">
import Navbar from '@/components/base/Navbar.vue'
import Footer from '@/components/base/Footer.vue'
import Notifications from '@/components/base/Notifications.vue'
import Notification, { IDialog, IToast } from '@/store/notifications'

export default {
  name: 'App',
  components: {
    Footer,
    Navbar,
    Notifications,
  },
  mounted() {
    // Example notifications:
    // Notification.openDialog({
    //   title: 'some title',
    //   content: 'some content',
    //   onConfirm: () => {
    //     console.log(confirm)
    //   },
    // } as IDialog)
    // Notification.toast({ message: 'some message' } as IToast)
  },
}
</script>

<style scoped lang="scss"></style>
