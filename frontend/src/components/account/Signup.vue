<template>
  <v-container class="d-flex align-center justify-center my-8">
    <v-card width="50rem">
      <v-card-title class="mb-4">Sign Up</v-card-title>
      <v-card-text>
        <form>
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="user.first_name"
                label="First Name"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="user.middle_name"
                label="Middle Name"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="user.last_name"
                label="Last Name"
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="user.email"
                label="Email (This will be your login username)"
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                type="password"
                v-model="user.password"
                label="Password"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                type="password"
                v-model="confirmPassword"
                label="Confirm Password"
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="user.address"
                label="Address (Optional)"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="user.phone"
                label="Phone (Optional)"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="user.organization"
                label="Organization (Optional)"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                v-model="user.type"
                label="User Type"
                :items="userTypes"
                outlined
                required
              ></v-autocomplete>
            </v-col>
          </v-row>
          <div class="mt-6">
            <v-btn-primary type="submit" @click="createUser"
              >Create User</v-btn-primary
            >
          </div>
        </form>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-text class="text-body-1">
        <span class="mr-2">Already have an account?</span>
        <router-link to="/login">Sign In</router-link>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/store/authentication'
import { User } from '@/types'
import { userTypes } from '@/vocabularies'

const confirmPassword = ref('')
const user = reactive<User>({
  id: '',
  email: '',
  password: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  phone: '',
  address: '',
  organization: '',
  type: '',
})

async function createUser() {
  if (user.password !== confirmPassword.value) {
    alert('Passwords do not match!')
    return
  }
  await useAuthStore().createUser(user)
}
</script>
