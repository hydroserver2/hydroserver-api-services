<template>
  <v-container class="d-flex align-center justify-center my-8">
    <v-card width="50rem">
      <v-card-title class="mb-4">Sign Up</v-card-title>
      <v-card-text>
        <v-form
          @submit.prevent="createUser"
          v-model="valid"
          ref="myForm"
          validate-on="blur"
        >
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="user.first_name"
                label="First Name"
                :rules="rules.requiredName"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="user.middle_name"
                label="Middle Name"
                :rules="user.middle_name ? rules.name : []"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="user.last_name"
                label="Last Name"
                :rules="rules.requiredName"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="user.email"
                label="Email (This will be your login username)"
                :rules="rules.email"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                type="password"
                v-model="user.password"
                label="Password"
                :rules="rules.password"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                type="password"
                v-model="confirmPassword"
                label="Confirm Password"
                :rules="rules.passwordMatch(user.password)"
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
                :rules="user.phone ? rules.phoneNumber : []"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="user.organization"
                label="Organization (Optional)"
                :rules="user.organization ? rules.maxLength(50) : []"
                validate-on="input"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                v-model="user.type"
                label="User Type"
                :items="userTypes"
                :rules="rules.required"
              ></v-autocomplete>
            </v-col>
          </v-row>
          <div class="mt-6">
            <v-btn-primary type="submit">Create User</v-btn-primary>
          </div>
        </v-form>
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
import { rules } from '@/utils/rules'
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/store/authentication'
import { User } from '@/types'
import { userTypes } from '@/vocabularies'
import { VForm } from 'vuetify/components'

const valid = ref(false)
const confirmPassword = ref('')
const myForm = ref<VForm>()
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
  if (!valid.value) return
  await useAuthStore().createUser(user)
}
</script>
