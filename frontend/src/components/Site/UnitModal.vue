<template>
  <v-dialog v-model="dialog" max-width="600px">
    <template v-slot:activator="{ on, attrs }">
      <v-btn color="primary" dark v-bind="attrs" @click="dialog = true"
        >Add Unit</v-btn
      >
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Add Unit</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="formData.name"
                label="Name"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.symbol"
                label="Symbol"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.definition"
                label="Definition"
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.unit_type"
                label="Unit Type"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="createUnit">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '@/store/data'

const emit = defineEmits(['unitCreated'])

const dataStore = useDataStore()
const dialog = ref(false)
const formData = ref({
  name: '',
  symbol: '',
  definition: '',
  unit_type: '',
})

async function createUnit() {
  try {
    const response = await this.$http.post('/units', formData.value)
    const newUnit = response.data
    dataStore.addUnit(newUnit)
    dialog.value = false
    emit('unitCreated', newUnit.id)
  } catch (error) {
    console.log('Error Registering Unit: ', error)
  }
}
</script>
