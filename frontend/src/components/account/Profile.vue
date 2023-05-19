<template>
  <v-container>
    <v-row class="text-center">
      <v-col>
        <h1>Profile</h1>
      </v-col>
    </v-row>

    <v-row class="text-left" v-if="authStore.user">
      <v-col>
        <h3>
          Welcome, {{ authStore.user.first_name }}
          {{ authStore.user.middle_name }}
          {{ authStore.user.last_name }}
        </h3>
        <div>{{ authStore.user.organization }}</div>
        <div>{{ authStore.user.address }}</div>
        <div>{{ authStore.user.phone }}</div>
        <div>{{ authStore.user.email }}</div>
      </v-col>
    </v-row>

    <v-row class="text-center">
      <v-col>
        <h3>
          Connect Account to
          <img class="hydroserver-logo" src="@/assets/hydro.png" alt="Hydro" />
        </h3>
        <v-btn color="primary">CONNECT</v-btn>
      </v-col>
    </v-row>

    <v-row class="text-center my-5">
      <v-col>
        <h4>What do you want to do?</h4>
      </v-col>
    </v-row>

    <v-row class="text-center">
      <v-col>
        <router-link to="/Sites">
          <img
            src="https://via.placeholder.com/150x150"
            alt="Manage My Sites"
          />
        </router-link>
        <div>Manage My Sites</div>
      </v-col>
      <v-col>
        <router-link to="/Browse">
          <img src="https://via.placeholder.com/150x150" alt="Browse Sites" />
        </router-link>
        <div>Browse Sites</div>
      </v-col>
      <v-col>
        <div>
          <img
            src="https://via.placeholder.com/150x150"
            alt="Edit My Profile"
          />
          <AccountModal />
        </div>

        <div>Edit My Profile</div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import AccountModal from '@/components/account/AccountModal.vue'
import { useAuthStore } from '@/store/authentication'

const authStore = useAuthStore()
</script>

<style scoped>
.hydroserver-logo {
  height: auto;
  max-height: 1.5rem;
}
</style>
