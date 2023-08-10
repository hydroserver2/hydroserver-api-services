<template>
  <v-container
    class="d-flex align-center justify-center py-8 fill-height login-container"
  >
    <v-card class="login-card" width="40rem">
      <v-card-title class="mb-4 login-title">Reset Password</v-card-title>
      <v-card-text>
        <v-form
          class="login-form"
          ref="myForm"
          @submit.prevent="resetPassword"
          v-model="valid"
        >
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                type="password"
                v-model="password"
                label="New Password"
                :rules="rules.password"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                type="password"
                v-model="confirmPassword"
                label="Confirm Password"
                :rules="rules.passwordMatch(password)"
              ></v-text-field>
            </v-col>
          </v-row>
          <div class="mt-6">
            <v-btn-primary type="submit">Reset Password</v-btn-primary>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { rules } from '@/utils/rules'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/authentication'

const valid = ref(false)
const myForm = ref(null)
const route = useRoute()
const password = ref('')
const confirmPassword = ref('')

const resetPassword = async () => {
  if (!valid.value) return
  await useAuthStore().resetPassword(
    route.params.uid.toString(),
    route.params.token.toString(),
    password.value
  )
}
</script>
