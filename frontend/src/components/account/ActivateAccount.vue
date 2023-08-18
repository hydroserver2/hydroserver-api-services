<template>
  <v-container class="d-flex align-center justify-center my-8">

  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { useRoute } from 'vue-router'

const authStore = useAuthStore()
const route = useRoute()

authStore.activateAccount(
  route.params.uid.toString(),
  route.params.token.toString()
)

</script>
