<template>
  <v-dialog v-model="dialog" activator="parent" max-width="600px">
    <v-card>
      <v-card-title>Edit Profile </v-card-title>
      <v-card-text>
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
          <v-col>
            <v-text-field
              v-model="user.phone"
              label="Phone Number"
              outlined
              required
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="user.address"
              label="Address"
              outlined
              required
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="user.organization"
              label="Organization"
              outlined
              required
            >
            </v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-autocomplete
              v-model="user.type"
              label="User Type"
              :items="userTypes"
              outlined
              required
            ></v-autocomplete>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="updateUser">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/store/authentication'
const authStore = useAuthStore()

const emit = defineEmits(['accountUpdated'])
const dialog = ref(false)
let user = reactive(authStore.user)

const userTypes = [
  'University Faculty',
  'University Professional or Research Staff',
  'Post-Doctoral Fellow',
  'University Graduate Student',
  'University Undergraduate Student',
  'Commercial/Professional',
  'Government Official',
  'School Student Kindergarten to 12th Grade',
  'School Teacher Kindergarten to 12th Grade',
  'Organization',
  'Other',
]

async function updateUser() {
  await authStore.updateUser(user)
  dialog.value = false
  emit('accountUpdated')
}
</script>
