<template>
  <v-container class="fill-height" fluid>
    <v-row class="justify-center align-center">
      <v-col cols="12" md="8">
        <v-card
          class="elevation-12 pa-6"
          max-width="600"
          style="
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
          "
        >
          <h2 class="mb-6">Sign Up</h2>
          <form>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="firstName"
                  label="First Name"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="middleName"
                  label="Middle Name"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="lastName"
                  label="Last Name"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="email"
                  label="Email (This will be your login username)"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  type="password"
                  v-model="password"
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
                  v-model="address"
                  label="Address (Optional)"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="phone"
                  label="Phone (Optional)"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="organization"
                  label="Organization (Optional)"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-autocomplete
                v-model="type"
                label="User Type"
                :items="userTypes"
                outlined
                required
              ></v-autocomplete>
            </v-row>
            <v-row class="mt-6">
              <v-col cols="12" md="6">
                <v-btn type="submit" color="primary" @click="submitForm"
                  >Create User</v-btn
                >
              </v-col>
            </v-row>
            <v-card-actions>
              <span class="mr-2">Already have an account</span>
              <router-link to="/login">Sign In</router-link>
            </v-card-actions>
          </form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import router from '@/router/router'
import { ref } from 'vue'

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const middleName = ref('')
const phone = ref('')
const address = ref('')
const organization = ref('')
const type = ref('')
const userTypes = ref([
  'University Faculty',
  'University Professional or Research Staff',
  'Post-Doctoral Fellow',
  'University Graduate Student',
  'University Undergraduate Student',
  'Commercial/Professional',
  'Government Official',
  'School Student Kindergarten to 12th Grade',
  'School Teacher Kindergarten to 12th Grade',
  'Organization',
  'Other',
])

async function submitForm() {
  if (password.value !== confirmPassword.value) {
    alert('Passwords do not match!')
    return
  }

  try {
    const response = await this.$http.post('/user', {
      first_name: firstName.value,
      last_name: lastName.value,
      email: email.value,
      password: password.value,
      middle_name: middleName.value,
      phone: phone.value,
      address: address.value,
      organization: organization.value,
      type: type.value,
    })
    const { access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    await router.push('/profile')
  } catch (error) {
    console.error(error)
  }
}
</script>
