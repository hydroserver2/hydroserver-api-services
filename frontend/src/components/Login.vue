<template>
  <v-row justify="center" align="center" style="height: 100%">
    <v-col cols="12" sm="8" md="4">
      <v-card class="elevation-12 semi-opaque light-text">
        <v-card-title class="headline light-text">Login</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="loginSubmit">
            <v-text-field
              label="Email"
              v-model="email"
              type="email"
              required
            ></v-text-field>
            <v-text-field
              label="Password"
              v-model="password"
              type="password"
              required
            ></v-text-field>
            <v-btn type="submit" color="primary" class="mr-4">Login</v-btn>
            <v-card-actions>
              <span class="mr-2">Don't have an account?</span>
              <router-link to="/signup" class="light-text">Sign Up</router-link>
            </v-card-actions>
          </v-form>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import { useAuthStore } from '@/store/authentication';
import {ref} from "vue";

export default {
  setup() {
    const authStore = useAuthStore();
    const email = ref('');
    const password = ref('');

    function loginSubmit() {
      authStore.login({
        email: email.value,
        password: password.value,
      });
    }

    return { email, password, loginSubmit };
  },
};
</script>

<style scoped>
.semi-opaque {
  background-color: rgba(0, 0, 0, 0.7);
  min-width: 30vw;
}

.light-text {
  color: #f5f5f5; /* Set the text color to a light shade */
}
</style>