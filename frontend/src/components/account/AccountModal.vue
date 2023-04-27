<template>
  <v-dialog v-model="dialog" activator="parent" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Edit Profile</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="user.first_name"
                label="First Name"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="user.middle_name"
                label="Middle Name"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="user.last_name"
                label="Last Name"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-text-field
              v-model="user.phone"
              label="Phone Number"
              outlined
              required
            ></v-text-field
          ></v-row>
          <v-row>
            <v-text-field
              v-model="user.address"
              label="Address"
              outlined
              required
            ></v-text-field
          ></v-row>
          <v-row>
            <v-text-field
              v-model="user.organization"
              label="Organization"
              outlined
              required
            ></v-text-field
          ></v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="updateUser">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { useDataStore } from '@/store/data.ts'
import { reactive, ref } from 'vue'
import axios from 'axios'

export default {
  name: 'AccountModal',
  setup(props, ctx) {
    const dataStore = useDataStore()
    const user = reactive({})
    const dialog = ref(false)

    dataStore.fetchOrGetFromCache('user', '/user').then(() => {
      Object.assign(user, dataStore.user)
    })

    function updateUser() {
      axios.patch('/user', user).then((response) => {
        const datastore = useDataStore()
        datastore.cacheProperty('user', response.data)
        dialog.value = false
        ctx.emit('accountUpdated')
      })
    }

    return { user, updateUser, dialog }
  },
}
</script>

<style scoped></style>
