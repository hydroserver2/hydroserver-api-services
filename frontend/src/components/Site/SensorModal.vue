<template>
  <v-dialog v-model="dialog" max-width="600px">
    <template v-slot:activator="{ on, attrs }">
      <v-btn color="primary" dark v-bind="attrs" @click="dialog = true"
        >Add Sensor</v-btn
      >
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Add Sensor</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" sm="6">
              <v-select
                v-model="formData.method_type"
                :items="allowedMethodTypes"
                label="Method Type"
                outlined
                required
              ></v-select>
            </v-col>
            <v-col cols="12" sm="6" v-if="!isSensorMethod">
              <v-text-field
                v-model="formData.name"
                label="Name"
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
            <v-col cols="12" sm="6" v-if="isSensorMethod">
              <v-text-field
                v-model="formData.manufacturer"
                label="Manufacturer"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6" v-if="isSensorMethod">
              <v-text-field
                v-model="formData.model"
                label="Model"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.encoding_type"
                label="Encoding Type"
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.model_url"
                label="Model URL"
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.method_link"
                label="Method Link"
                outlined
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formData.method_code"
                label="Method Code"
                outlined
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="createSensor">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { computed, ref } from 'vue'
import axios from '@/plugins/axios.config'
import { useDataStore } from '@/store/data'

export default {
  setup(props, ctx) {
    const dataStore = useDataStore()
    const dialog = ref(false)
    const formData = ref({
      manufacturer: '',
      model: '',
      name: '',
      description: '',
      encoding_type: '',
      model_url: '',
      method_link: '',
      method_code: '',
      method_type: 'Instrument Deployment',
    })
    const allowedMethodTypes = ref([
      'Derivation',
      'Estimation',
      'Instrument Deployment',
      'Observation',
      'Simulation',
      'Specimen Analysis',
      'Unknown',
    ])

    const isSensorMethod = computed(
      () => formData.value.method_type === 'Instrument Deployment'
    )

    function createSensor() {
      if (
        formData.value.method_type === 'Instrument Deployment' &&
        formData.value.manufacturer &&
        formData.value.model
      ) {
        formData.value.name =
          formData.value.manufacturer + ': ' + formData.value.model
      }
      axios
        .post('/sensors', formData.value)
        .then((response) => {
          const newSensor = response.data
          dataStore.addSensor(newSensor)
          dialog.value = false
          ctx.emit('sensorCreated', String(newSensor.id))
        })
        .catch((error) => {
          console.log('Error Registering Sensor: ', error)
        })
    }

    return {
      formData,
      dialog,
      allowedMethodTypes,
      isSensorMethod,
      createSensor,
    }
  },
}
</script>
