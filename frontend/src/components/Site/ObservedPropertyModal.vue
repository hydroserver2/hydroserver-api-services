<template>
  <v-dialog v-model="dialog" max-width="600px">
    <template v-slot:activator="{ on, attrs }">
      <v-btn color="primary" dark v-bind="attrs" @click="dialog = true"
        >Add Observed Property</v-btn
      >
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Add Observed Property</span>
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
                v-model="formData.definition"
                label="Definition"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.description"
                label="Description"
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="formData.variable_type"
                label="Variable Type"
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="formData.variable_code"
                label="Variable Code"
                outlined
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="createObservedProperty"
          >Submit</v-btn
        >
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
      definition: '',
      description: '',
      variable_type: '',
      variable_code: '',
    })

    function createObservedProperty() {
      axios
        .post('/observed-properties', formData.value)
        .then((response) => {
          const newObservedProperty = response.data
          dataStore.addObservedProperty(newObservedProperty)
          dialog.value = false
          ctx.emit('observedPropertyCreated', String(newObservedProperty.id))
        })
        .catch((error) => {
          console.log('Error Registering Observed Property: ', error)
        })
    }

    return { formData, dialog, createObservedProperty }
  },
}
</script>
