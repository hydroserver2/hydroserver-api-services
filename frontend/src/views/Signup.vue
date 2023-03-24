<template>
  <h2>Sign up Page</h2>
  <form @submit.prevent="submitForm">
    <label>
      First Name:
      <input type="text" v-model="firstName" required>
    </label>
    <label>
      Last Name:
      <input type="text" v-model="lastName" required>
    </label>
    <label>
      Email:
      <input type="email" v-model="email" required>
    </label>
    <label>
      Password:
      <input type="password" v-model="password" required>
    </label>
    <label>
      Confirm Password:
      <input type="password" v-model="confirmPassword" required>
    </label>
    <label>
      Middle Name:
      <input type="text" v-model="middleName">
    </label>
    <label>
      Phone:
      <input type="tel" v-model="phone">
    </label>
    <label>
      Address:
      <input type="text" v-model="address">
    </label>
    <button type="submit">Create User</button>
  </form>
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