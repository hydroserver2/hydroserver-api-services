<template>
  <v-container>
    <v-row v-if="authStore.user">
      <v-col cols="12">
        <v-row>
          <v-col>
            <v-card color="surface" elevation="2">
              <v-row no-gutters>
                <v-col
                  cols="12"
                  md="auto"
                  class="d-flex align-center justify-center primary"
                  style="background-color: #2196f3"
                >
                  <v-card-title :style="{ color: 'white' }">
                    <h5 class="text-h5">
                      {{ authStore.user.first_name }}
                      {{ authStore.user.middle_name }}
                      {{ authStore.user.last_name }}
                    </h5>
                  </v-card-title>
                </v-col>

                <v-col cols="auto" class="pl-2 pt-2 pb-2">
                  <table>
                    <tbody>
                      <tr>
                        <td class="pr-4"><strong>Organization</strong></td>
                        <td>{{ authStore.user.organization }}</td>
                      </tr>
                      <tr>
                        <td class="pr-4"><strong>Address</strong></td>
                        <td>{{ authStore.user.address }}</td>
                      </tr>
                      <tr>
                        <td class="pr-4"><strong>Phone</strong></td>
                        <td>{{ authStore.user.phone }}</td>
                      </tr>
                      <tr>
                        <td class="pr-4"><strong>Email</strong></td>
                        <td>{{ authStore.user.email }}</td>
                      </tr>
                    </tbody>
                  </table>
                </v-col>
              </v-row>
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="6">
            <v-card
              class="d-flex align-center"
              @click="editAccountDialog = true"
              color="surface"
              elevation="2"
            >
              <v-card-text class="text--primary">
                <div class="d-flex justify-content-between">
                  <span class="text-truncate">Edit My Profile</span>
                  <v-spacer></v-spacer>
                  <v-icon color="primary" large
                    >mdi-account-edit-outline</v-icon
                  >
                </div>
              </v-card-text>
            </v-card>
            <v-dialog v-model="editAccountDialog" max-width="40rem">
              <AccountModal @close="editAccountDialog = false"></AccountModal>
            </v-dialog>
          </v-col>
          <v-col cols="6">
            <v-card
              class="d-flex align-center"
              @click="deleteAccountDialog = true"
              color="surface"
              elevation="2"
            >
              <v-card-text class="text--primary">
                <div class="d-flex justify-content-between">
                  <span class="text-truncate">Delete Account</span>
                  <v-spacer></v-spacer>
                  <v-icon color="error" large>mdi-account-remove</v-icon>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
      <v-spacer></v-spacer>
      <v-col cols="12" md="6" class="justify-center text-center">
        <v-card color="white" elevation="2" @click="$router.push('/Sites')">
          <v-container style="background-color: #eeeeee">
            <v-responsive>
              <img
                style="max-height: 100%; max-width: 100%; object-fit: contain"
                src="@/assets/CUAHSI.png"
                alt="CUAHSI Logo"
              />
            </v-responsive>
          </v-container>
          <v-card-title class="text-wrap"
            >Connect Account to HydroShare</v-card-title
          >
          <v-card-actions class="justify-center">
            <v-btn-primary>CONNECT</v-btn-primary>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- <v-row class="justify-center text-center"> </v-row>

    <v-row class="text-center my-5">
      <v-col>
        <h5 class="text-h5">What do you want to do?</h5>
      </v-col>
    </v-row> -->
    <!-- <v-row> -->
    <!-- <v-col>
        <v-card
          class="d-flex align-center"
          @click="$router.push('/Sites')"
          color="surface"
          elevation="2"
        >
          <v-card-text class="text--primary">
            <div class="d-flex justify-content-between">
              <span class="text-truncate">Manage My Sites</span>
              <v-spacer></v-spacer>
              <v-icon color="primary" large>mdi-domain</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col> -->

    <!-- <v-col>
        <v-card
          class="d-flex align-center"
          @click="$router.push('/Browse')"
          color="surface"
          elevation="2"
        >
          <v-card-text class="text--primary">
            <div class="d-flex justify-content-between">
              <span class="text-truncate">Browse Sites</span>
              <v-spacer></v-spacer>
              <v-icon color="primary" large>mdi-magnify</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col> -->
    <!-- </v-row> -->
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
const editAccountDialog = ref(false)
const deleteInput = ref('')

async function deleteAccount() {
  if (deleteInput.value.toLowerCase() !== 'delete my account and data') {
    Notification.toast({ message: "input doesn't match", type: 'error' })
    return
  }
  await authStore.deleteAccount()
  deleteAccountDialog.value = false
}

onMounted(async () => {
  await thingStore.fetchThings()
})
</script>
