<template>
  <div style="margin: 1rem">
    <h3>{{ datastreamId ? 'Edit Datastream' : 'Datastream Setup' }} Page</h3>
    <v-autocomplete
      v-if="!datastreamId"
      v-model="selectedDatastream"
      label="Start from an existing datastream"
      :items="formattedDatastream"
      item-value="id"
    ></v-autocomplete>

    <div>
      <v-form @submit.prevent="uploadDatastream">
        <v-container>
          <v-row style="margin-bottom: 1rem">
            <v-col cols="12" md="3">
              <v-autocomplete
                v-model="selectedSensor"
                label="Select sensor"
                :items="sensors"
                item-title="name"
                item-value="id"
                no-data-text="No available sensors"
              ></v-autocomplete>
              <sensor-modal @sensorCreated="updateSensors"></sensor-modal>
            </v-col>
            <v-col cols="12" md="3">
              <v-autocomplete
                v-model="selectedObservedProperty"
                label="Select observed property"
                :items="observedProperties"
                item-title="name"
                item-value="id"
                no-data-text="No available properties"
              ></v-autocomplete>
              <observed-property-modal
                @observedPropertyCreated="updateObservedProperties"
                >Add New</observed-property-modal
              >
            </v-col>
            <v-col cols="12" md="3">
              <v-autocomplete
                v-model="selectedUnit"
                label="Select unit"
                :items="units"
                item-title="name"
                item-value="id"
                no-data-text="No available units"
              ></v-autocomplete>
              <unit-modal @unitCreated="updateUnits">Add New</unit-modal>
            </v-col>
            <v-col cols="12" md="3">
              <v-autocomplete
                v-model="selectedProcessingLevel"
                label="Select processing level"
                :items="formattedProcessingLevels"
                item-value="id"
                no-data-text="No available processing level"
              ></v-autocomplete>
              <processing-level-modal
                @processingLevelCreated="updateProcessingLevels"
                >Add New</processing-level-modal
              >
            </v-col>
          </v-row>

          <v-text-field
            v-model="ds_sampled_medium"
            label="Sampled medium"
            :rules="[(v) => !!v || 'Sampled medium is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_status"
            label="Status"
            :rules="[(v) => !!v || 'Status is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_no_data_value"
            label="No data value"
            :rules="[(v) => !!v || 'No data value is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_aggregation_statistic"
            label="Aggregation statistic"
            :rules="[(v) => !!v || 'Aggregation statistic is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_result_type"
            label="Result type"
          ></v-text-field>
          <v-text-field
            v-model="ds_observation_type"
            label="Observation type"
          ></v-text-field>

          <v-btn type="submit" color="green">{{
            datastreamId ? 'Update' : 'Save'
          }}</v-btn>
        </v-container>
      </v-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useDataStore } from '@/store/data'
import { useRoute } from 'vue-router'
import SensorModal from '@/components/Site/SensorModal.vue'
import ObservedPropertyModal from '@/components/Site/ObservedPropertyModal.vue'
import UnitModal from '@/components/Site/UnitModal.vue'
import ProcessingLevelModal from '@/components/Site/ProcessingLevelModal.vue'
import axios from '@/plugins/axios.config'
import router from '@/router/router'

const dataStore = useDataStore()
const route = useRoute()
const thingId = route.params.id
const datastreamId = route.params.datastreamId

let selectedDatastream = ref(null)
const datastreams = ref([])

let selectedUnit = ref(null)
let selectedObservedProperty = ref(null)
let selectedSensor = ref(null)
let selectedProcessingLevel = ref(null)

let units = ref([])
let observedProperties = ref([])
let sensors = ref([])
let processingLevels = ref([])

const ds_sampled_medium = ref('')
const ds_status = ref('')
const ds_no_data_value = ref('')
const ds_aggregation_statistic = ref('')
const ds_result_type = ref('')
const ds_observation_type = ref('')

const formattedDatastream = computed(() => {
  return datastreams.value.map((datastream) => ({
    id: datastream.id,
    title: `${datastream.method_name} : ${datastream.observed_property_name} : ${datastream.unit_name} : ${datastream.processing_level_name}`,
  }))
})

const formattedProcessingLevels = computed(() => {
  return processingLevels.value.map((pl) => ({
    id: pl.id,
    title: `${pl.processing_level_code} : ${pl.definition}`,
  }))
})

async function updateSensors(newSensorID) {
  await dataStore.fetchOrGetFromCache('sensors', '/sensors')
  sensors.value = dataStore.sensors
  selectedSensor.value = newSensorID
}

async function updateObservedProperties(newObservedPropertyId) {
  await dataStore.fetchOrGetFromCache(
    'observedProperties',
    '/observed-properties'
  )
  observedProperties.value = dataStore.observedProperties
  selectedObservedProperty.value = newObservedPropertyId
}

async function updateUnits(newUnitId) {
  await dataStore.fetchOrGetFromCache('units', '/units')
  units.value = dataStore.units.sort((a, b) => a.name.localeCompare(b.name))
  selectedUnit.value = newUnitId
}

async function updateProcessingLevels(newProcessingLevelId) {
  await dataStore.fetchOrGetFromCache('processingLevels', '/processing-levels')
  processingLevels.value = dataStore.processingLevels
  selectedProcessingLevel.value = newProcessingLevelId
}

async function populateDatastreamSelector(newDatastreamId) {
  await dataStore.fetchOrGetFromCache('datastreams', '/datastreams')
  datastreams.value = dataStore.datastreams
  selectedDatastream.value = newDatastreamId
}

async function populateDatastream(selectedDatastreamId = null) {
  if (selectedDatastreamId === null) selectedDatastreamId = datastreamId
  const datastream = datastreams.value.find(
    (ds) => ds.id === selectedDatastreamId
  )
  if (datastream) populateForm(datastream)
}

watch(selectedDatastream, () => {
  populateDatastream(selectedDatastream.value)
})

updateSensors()
updateObservedProperties()
updateUnits()
updateProcessingLevels()

if (datastreamId) populateDatastream()
else populateDatastreamSelector()

function populateForm(datastream) {
  selectedSensor.value = datastream.method_id
  selectedObservedProperty.value = datastream.observed_property_id
  selectedUnit.value = datastream.unit_id
  selectedProcessingLevel.value = datastream.processing_level_id

  ds_sampled_medium.value = datastream.sampled_medium
  ds_status.value = datastream.status
  ds_no_data_value.value = datastream.no_data_value
  ds_aggregation_statistic.value = datastream.aggregation_statistic
  ds_result_type.value = datastream.result_type
  ds_observation_type.value = datastream.observation_type
}

async function uploadDatastream() {
  try {
    const payload = {
      thing_id: thingId,
      sensor: String(selectedSensor.value),
      observed_property: String(selectedObservedProperty.value),
      unit: String(selectedUnit.value),
      processing_level: String(selectedProcessingLevel.value),
      sampled_medium: ds_sampled_medium.value,
      status: ds_status.value,
      no_data_value: ds_no_data_value.value,
      aggregation_statistic: ds_aggregation_statistic.value,
      result_type: ds_result_type.value,
      observation_type: ds_observation_type.value,
    }
    if (datastreamId) {
      await axios.put(`/datastreams/${datastreamId}`, payload)
    } else {
      const response = await axios.post('/datastreams', payload)
      const newDatastream = response.data
      dataStore.addDatastream(newDatastream)
    }
    localStorage.removeItem(`thing_${thingId}`)
    await router.push({ name: 'SiteDatastreams', params: { id: thingId } })
  } catch (error) {
    console.log('Error Registering Datastream: ', error)
  }
}
</script>
