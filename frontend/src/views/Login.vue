<template>
  <div class="container">
    <h1>Login</h1>
    <form @submit.prevent="Login">
      <div class="form-group">
        <label for="email">Email address</label>
        <input type="email" class="form-control" id="email" v-model="email" required>
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" class="form-control" id="password" v-model="password" required>
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    <div>
      <span>Don't have an account?</span>
      <router-link to="/signup">Sign Up</router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import store from "../store.js";

export default {
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    async Login() {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/token', {
            username: this.email,
            password: this.password
          });
        console.log(response.data)
        const { access_token, refresh_token } = response.data;
        store.commit("setAccessToken", access_token)
        store.commit("setRefreshToken", refresh_token)
        await this.$router.push({ name: "Sites" });
      } catch (error) {
        console.error(error)
      }
    }
  }
}
</script>