<template>
  <div class="container">
    <h1>Login</h1>
    <form @submit.prevent="loginSubmit">
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
import {mapActions} from "vuex";

export default {
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    ...mapActions([
      'login'
    ]),
    loginSubmit() {
      this.login({
        email: this.email,
        password: this.password
      });
    }
  }
}
</script>