<template>
  <v-container
    class="d-flex align-center justify-center py-8 fill-height login-container"
  >
    <v-card class="login-card" width="40rem">
      <v-card-title class="mb-4 login-title">Sign In</v-card-title>
      <v-card-text>
        <v-form class="login-form" ref="form" v-model="valid">
          <v-text-field
            class="mb-4 email-input"
            label="Email"
            autofocus
            v-model="email"
            :rules="rules.email"
            type="email"
            name="email"
            validate-on="blur"
          ></v-text-field>
          <v-text-field
            class="mb-4 password-input"
            label="Password"
            :rules="rules.required"
            v-model="password"
            type="password"
            name="password"
          ></v-text-field>
          <v-btn-primary
            class="login-button mr-4"
            :disabled="!valid"
            type="submit"
            @submit.prevent="loginSubmit"
            >Log In</v-btn-primary
          >
        </v-form>
      </v-card-text>
      <v-divider class="login-divider"></v-divider>
      <v-card-actions class="text-body-1 signup-link-section">
        <span class="mr-2">Don't have an account?</span>
        <router-link to="/signup" class="light-text signup-link"
          >Sign Up</router-link
        >
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'
import { ref } from 'vue'
import { rules } from '@/utils/rules'

const email = ref('')
const password = ref('')
const form = ref(null)
const valid = ref(false)

const loginSubmit = async () => {
  if (!valid) return
  await useAuthStore().login(email.value, password.value)
}
</script>

<style scoped lang="scss"></style>
