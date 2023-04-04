<template>
  <v-container class="fill-height" fluid>
    <v-row class="justify-center align-center">
      <v-col cols="12" md="8">
        <v-card class="elevation-12 pa-6" max-width="600" style="background: rgba(255,255,255,0.8); backdrop-filter: blur(10px);">
<!--          <v-img src="src/assets/dam-background.jpg" height="250px" width="100%" class="mb-6"></v-img>-->
          <h2 class="mb-6">Sign Up</h2>
          <form @submit.prevent="submitForm">
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field v-model="firstName" label="First Name" required></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="middleName" label="Middle Name"></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="lastName" label="Last Name" required></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="email" label="Email" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="password" label="Password" required></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="address" label="Address"></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="phone" label="Phone"></v-text-field>
              </v-col>
            </v-row>
            <v-row class="mt-6">
              <v-col cols="12" md="6">
                <v-btn type="submit" color="primary">Create User</v-btn>
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

<script>
import axios from 'axios'

export default {
  data() {
    return {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      middleName: '',
      phone: '',
      address: '',
    }
  },
  methods: {
    async submitForm() {
      if (this.password !== this.confirmPassword) {
        alert('Passwords do not match!')
        return
      }

      try {
        const response = await axios.post('/user', {
          first_name: this.firstName,
          last_name: this.lastName,
          email: this.email,
          password: this.password,
          middle_name: this.middleName,
          phone: this.phone,
          address: this.address,
        })
        console.log('Created user:', response.data)
      } catch (error) {
        console.error(error)
      }
    },
  },
}
</script>