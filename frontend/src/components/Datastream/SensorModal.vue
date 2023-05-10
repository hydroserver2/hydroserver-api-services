<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ isEdit ? 'Edit' : 'Add' }} Sensor</span>
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
      <v-btn color="blue darken-1" text @click="$emit('close')">Cancel</v-btn>
      <v-btn color="blue darken-1" text @click="uploadSensor">{{
        isEdit ? 'Update' : 'Save'
      }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import axios from '@/plugins/axios.config'
import { useDataStore } from '@/store/data'

const props = defineProps({
  sensor: { type: Object, default: null },
})

const isEdit = computed(() => {
  return props.sensor != null
})

const dataStore = useDataStore()
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

onMounted(() => {
  if (isEdit.value) {
    formData.value = {
      manufacturer: props.sensor.manufacturer || '',
      model: props.sensor.model || '',
      name: props.sensor.name || '',
      description: props.sensor.description || '',
      encoding_type: props.sensor.encoding_type || '',
      model_url: props.sensor.model_url || '',
      method_link: props.sensor.method_link || '',
      method_code: props.sensor.method_code || '',
      method_type: props.sensor.method_type || 'Instrument Deployment',
    }
  }
})

const isSensorMethod = computed(
  () => formData.value.method_type === 'Instrument Deployment'
)

const emit = defineEmits(['uploaded', 'close'])

async function uploadSensor() {
  if (
    formData.value.method_type === 'Instrument Deployment' &&
    formData.value.manufacturer &&
    formData.value.model
  ) {
    formData.value.name =
      formData.value.manufacturer + ': ' + formData.value.model
  }
  try {
    if (isEdit.value) {
      await axios.patch(`/sensors/${props.sensor.id}`, formData.value)
      localStorage.removeItem(`sensors`)
      dataStore.sensors = []
      emit('uploaded', String(props.sensor.id))
    } else {
      const response = await axios.post('/sensors', formData.value)
      const newSensor = response.data
      dataStore.addSensor(newSensor)
      emit('uploaded', String(newSensor.id))
    }
    emit('close')
  } catch (error) {
    console.log('Error Registering Sensor: ', error)
  }
}
</script>
