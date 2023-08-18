<template>
  <v-container class="d-flex align-center justify-center my-8">
    <v-card width="50rem">
      <v-card-title class="mb-4 signup-title">Verify Your Email</v-card-title>
      <v-card-text>
        Before you continue, we need to verify the email address you provided for your account.
      </v-card-text>
      <v-card-text>
        We've sent an email to <b>{{authStore.user.email}}</b>. Click on the link in that message to verify your
        email address and activate your HydroServer account.
      </v-card-text>
      <v-card-text>
        NOTE: The verification email may take several minutes to arrive in your inbox.
      </v-card-text>
      <v-divider></v-divider>
      <v-card-text class="text-body-1">
        <span class="mr-2">Didn't receive a verification email?</span>
        <button
          :disabled="authStore.sendingVerificationEmail"
          @click="authStore.sendVerificationEmail()"
        >
          <a>Resend Email</a>
        </button>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/authentication'

const authStore = useAuthStore()

</script>
