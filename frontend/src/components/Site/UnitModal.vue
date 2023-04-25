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

<script lang="ts">
import { ref } from 'vue'
import axios from '@/axios.config'
import { useDataStore } from '@/store/data'

export default {
  setup(props, ctx) {
    const dataStore = useDataStore()
    const dialog = ref(false)
    const formData = ref({
      name: '',
      symbol: '',
      definition: '',
      unit_type: '',
    })

    function createUnit() {
      axios
        .post('/units', formData.value)
        .then((response) => {
          const newUnit = response.data
          dataStore.addUnit(newUnit)
          dialog.value = false
          ctx.emit('unitCreated', newUnit.id)
        })
        .catch((error) => {
          console.log('Error Registering Unit: ', error)
        })
    }

    return { formData, dialog, createUnit }
  },
}
</script>
