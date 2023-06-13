<template>
  <v-container>
    <v-row class="text-center">
      <v-col>
        <h3 class="text-h3">Profile</h3>
      </v-col>
    </v-row>

    <v-row class="text-left" v-if="authStore.user">
      <v-col>
        <h3>
          {{ authStore.user.first_name }}
          {{ authStore.user.middle_name }}
          {{ authStore.user.last_name }}
        </h3>
        <div>{{ authStore.user.organization }}</div>
        <div>{{ authStore.user.address }}</div>
        <div>{{ authStore.user.phone }}</div>
        <div>{{ authStore.user.email }}</div>
      </v-col>
    </v-row>

    <v-row class="justify-center text-center">
      <v-col cols="12">
        <v-row class="justify-center">
          <v-col class="align-center" cols="auto">
            <h5 class="text-h5">Connect Account to</h5>
          </v-col>
          <v-col cols="auto">
            <img
              class="hydroserver-logo"
              src="@/assets/hydro.png"
              alt="Hydro"
            />
          </v-col>
        </v-row>
        <v-btn-primary>CONNECT</v-btn-primary>
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
          <v-icon color="black" large>mdi-domain</v-icon>
        </router-link>
        <div>Manage My Sites</div>
      </v-col>
      <v-col>
        <router-link to="/Browse">
          <v-icon color="black" large>mdi-magnify</v-icon>
        </router-link>
        <div>Browse Sites</div>
      </v-col>
      <v-col>
        <div>
          <v-icon large>mdi-account-edit-outline</v-icon>
          <AccountModal />
        </div>
        <div>Edit My Profile</div>
      </v-col>
      <v-col>
        <v-icon large @click="deleteAccountDialog = true"
          >mdi-account-remove</v-icon
        >
        <div>Delete Account</div>
      </v-col>
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
        <v-btn-cancel @click="deleteAccountDialog = false">Cancel</v-btn-cancel>
        <v-btn color="delete" text @click="deleteAccount">Delete</v-btn>
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
    Notification.toast({ message: "input doesn't match", type: 'error' })
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
