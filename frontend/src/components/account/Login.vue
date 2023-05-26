<template>
  <v-container class="d-flex align-center justify-center py-8 fill-height">
    <v-card width="40rem">
      <v-card-title class="mb-4">Sign In</v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="loginSubmit" v-model="valid">
          <v-text-field
            class="mb-4"
            label="Email"
            autofocus
            v-model="email"
            :rules="rules.email"
            type="email"
            name="email"
            required
          ></v-text-field>
          <v-text-field
            class="mb-4"
            label="Password"
            :rules="rules.password"
            v-model="password"
            type="password"
            name="password"
            required
          ></v-text-field>
          <v-btn-primary
            :disabled="!valid"
            type="submit"
            color="primary"
            class="mr-4"
            >Log In</v-btn-primary
          >
        </v-form>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions class="text-body-1">
        <span class="mr-2">Don't have an account?</span>
        <router-link to="/signup" class="light-text">Sign Up</router-link>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { ref } from 'vue'

const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const form = ref(null)
const valid = ref(false)
const rules = {
  password: [
    (value: string) => {
      if (value) return true

      return 'Password is required.'
    },
    // (value: string) => {
    //   if (value?.length <= 6) return true

    //   return 'Password must be 6 characters or longer.'
    // },
  ],
  email: [
    (value: string) => {
      if (value) return true

      return 'Email is required.'
    },
    (value: string) => {
      if (/.+@.+\..+/.test(value)) return true

      return 'Email must be valid.'
    },
  ],
}

const loginSubmit = async () => {
  if (valid) {
    await authStore.login(email.value, password.value)
  }
}
</script>

<style scoped lang="scss"></style>
