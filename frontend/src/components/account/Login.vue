<template>
  <v-card>
    <v-card-title>Sign In!</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="loginSubmit">
        <v-text-field
          label="Email"
          v-model="email"
          type="email"
          required
        ></v-text-field>
        <v-text-field
          label="Password"
          v-model="password"
          type="password"
          required
        ></v-text-field>
        <v-btn type="submit" color="primary" class="mr-4">Login</v-btn>
        <v-card-actions>
          <span class="mr-2">Don't have an account?</span>
          <router-link to="/signup" class="light-text">Sign Up</router-link>
        </v-card-actions>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { ref } from 'vue'

const authStore = useAuthStore()
const email = ref('')
const password = ref('')

function loginSubmit() {
  authStore.login({
    email: email.value,
    password: password.value,
  })
}
</script>

<style scoped lang="scss"></style>
