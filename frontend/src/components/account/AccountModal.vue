<template>
  <v-card>
    <v-card-title>Edit Profile </v-card-title>
    <v-card-text>
      <v-form
        ref="myForm"
        v-model="valid"
        validate-on="blur"
        @submit.prevent="updateUser"
      >
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="user.first_name"
              label="First Name"
              :rules="rules.requiredName"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="user.middle_name"
              label="Middle Name"
              :rules="rules.name"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="user.last_name"
              label="Last Name"
              :rules="rules.requiredName"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="user.phone"
              v-maska:[phoneMask]
              label="Phone Number"
              :rules="rules.phoneNumber"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field v-model="user.address" label="Address"></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="user.organization"
              label="Organization"
              :rules="rules.maxLength(50)"
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
              :rules="rules.required"
            ></v-autocomplete>
          </v-col>
        </v-row>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn-cancel @click="closeDialog">Cancel</v-btn-cancel>
          <v-btn type="submit">Update</v-btn>
        </v-card-actions>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { rules } from '@/utils/rules'
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/authentication'
import { userTypes } from '@/vocabularies'
import { VForm } from 'vuetify/components'
import { vMaska } from 'maska'

const phoneMask = { mask: '(###) ###-####' }
const authStore = useAuthStore()
let user = reactive({ ...authStore.user })
const valid = ref(false)
const myForm = ref<VForm>()

const emit = defineEmits(['close'])
const closeDialog = () => emit('close')

const updateUser = async () => {
  await myForm.value?.validate()
  if (!valid.value) return
  await authStore.updateUser(user)
  emit('close')
}

onMounted(async () => await myForm.value?.validate())
</script>
