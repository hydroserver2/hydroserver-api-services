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
              v-model="sensor.method_type"
              :items="methodTypes"
              label="Method Type"
              outlined
              required
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6" v-if="!isInstrument">
            <v-text-field
              v-model="sensor.name"
              label="Name"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="sensor.description"
              label="Description"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" v-if="isInstrument">
            <v-text-field
              v-model="sensor.manufacturer"
              label="Manufacturer"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" v-if="isInstrument">
            <v-text-field
              v-model="sensor.model"
              label="Model"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="sensor.encoding_type"
              label="Encoding Type"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="sensor.model_url"
              label="Model URL"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="sensor.method_link"
              label="Method Link"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="sensor.method_code"
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
import { computed, onMounted, reactive } from 'vue'
import { useSensorStore } from '@/store/sensors'
import { Sensor } from '@/types'
import { methodTypes } from '@/vocabularies'

const sensorStore = useSensorStore()
const props = defineProps({ id: String })
const isEdit = computed(() => props.id != null)
const emit = defineEmits(['uploaded', 'close'])

const sensor = reactive<Sensor>({
  id: '',
  name: '',
  description: '',
  manufacturer: '',
  model: '',
  method_type: 'Instrument Deployment',
  method_code: '',
  method_link: '',
  encoding_type: '',
  model_url: '',
})

const isInstrument = computed(
  () => sensor.method_type === 'Instrument Deployment'
)

async function uploadSensor() {
  if (
    sensor.method_type === 'Instrument Deployment' &&
    sensor.manufacturer &&
    sensor.model
  ) {
    sensor.name = sensor.manufacturer + ': ' + sensor.model
  }

  if (isEdit.value) await sensorStore.updateSensor(sensor)
  else {
    const newSensor = await sensorStore.createSensor(sensor)
    emit('uploaded', String(newSensor.id))
  }
  emit('close')
}

onMounted(async () => {
  await sensorStore.fetchSensors()
  if (props.id) Object.assign(sensor, await sensorStore.getSensorById(props.id))
})
</script>
