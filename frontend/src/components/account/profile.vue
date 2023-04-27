<template>
  <v-container>
    <v-row class="text-center">
      <v-col>
        <h1>Profile</h1>
      </v-col>
    </v-row>

    <v-row class="text-left">
      <v-col>
        <h3>
          Welcome, {{ user.first_name }} {{ user.middle_name }}
          {{ user.last_name }}
        </h3>
        <div>{{ user.organization }}</div>
        <div>{{ user.address }}</div>
        <div>{{ user.phone }}</div>
        <div>{{ user.email }}</div>
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
          <account-modal @accountUpdated="loadAccount" />
        </div>

        <div>Edit My Profile</div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useDataStore } from '@/store/data.ts'
import { reactive, ref } from 'vue'
import AccountModal from '@/components/account/AccountModal.vue'

export default {
  name: 'Profile',
  components: { AccountModal },
  setup() {
    const dataStore = useDataStore()
    let user = reactive({})

    function loadAccount() {
      dataStore.fetchOrGetFromCache('user', '/user').then(() => {
        console.log('Updated User:', dataStore.user)
        Object.assign(user, dataStore.user)
      })
    }
    loadAccount()

    return { user, loadAccount }
  },
}
</script>

<style scoped>
.hydroserver-logo {
  height: auto;
  max-height: 1.5rem;
}
</style>
