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
    <v-row>
      <v-btn @click="deleteAccountDialog = true"> Delete Account</v-btn>
    </v-row>
  </v-container>

  <v-dialog v-model="deleteAccountDialog" width="40rem">
    <v-card>
      <v-card-title class="headline">Confirm Account Deletion</v-card-title>
      <v-card-text>
        Are you sure you want to delete your account? This action will
        permanently remove all your information from the system including all
        sites, datastreams, and observations you have primary ownership of, user
        information, and preferences. This action cannot be undone.
      </v-card-text>
      <v-card-text v-if="thingStore.primaryOwnedThings.length > 0">
        The following is a list of the sites you have primary ownership of that
        will be deleted with your account. If you have secondary owners, we
        strongly recommend transferring primary ownership to one of them before
        deleting your account. Additionally, you have the option to store your
        site data in hydroshare or download your data before deleting your
        account.
      </v-card-text>
      <v-card-text>
        <div v-for="thing in thingStore.primaryOwnedThings">
          {{ thing.name }}
        </div>
      </v-card-text>

      <v-card-text>
        Please type the following text to confirm deletion:
        <strong> Delete my account and data </strong>
        <v-form>
          <v-text-field
            v-model="deleteInput"
            solo
            @keydown.enter.prevent="deleteAccount"
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="green darken-1" text @click="deleteAccountDialog = false"
          >Cancel</v-btn
        >
        <v-btn color="red darken-1" text @click="deleteAccount">Delete</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import AccountModal from '@/components/account/AccountModal.vue'
import { useAuthStore } from '@/store/authentication'
import { onMounted, ref } from 'vue'
import Notification from '@/store/notifications'
import { useThingStore } from '@/store/things'

const authStore = useAuthStore()
const thingStore = useThingStore()

const deleteAccountDialog = ref(false)
const deleteInput = ref('')

async function deleteAccount() {
  if (deleteInput.value.toLowerCase() !== 'delete my account and data') {
    Notification.toast({ message: "input doesn't match" })
    return
  }
  console.log('deleting account')
  await authStore.deleteAccount()
  deleteAccountDialog.value = false
}

onMounted(async () => {
  await thingStore.fetchThings()
})
</script>

<style scoped>
.hydroserver-logo {
  height: auto;
  max-height: 1.5rem;
}
</style>
