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
              <v-btn
                variant="elevated"
                density="comfortable"
                color="green"
                @click="showSensorModal = true"
                prependIcon="mdi-plus"
                >Add New</v-btn
              >
              <v-dialog v-model="showSensorModal" width="60rem">
                <sensor-modal
                  @uploaded="updateSensors"
                  @close="showSensorModal = false"
                ></sensor-modal>
              </v-dialog>
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
              <v-dialog v-model="showObservedPropertyModal" width="60rem">
                <ObservedPropertyModal
                  @uploaded="updateObservedProperties"
                  @close="showObservedPropertyModal = false"
                ></ObservedPropertyModal>
              </v-dialog>
              <v-btn
                variant="elevated"
                density="comfortable"
                color="green"
                @click="showObservedPropertyModal = true"
                prependIcon="mdi-plus"
                >Add New</v-btn
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
              <v-btn
                variant="elevated"
                density="comfortable"
                color="green"
                @click="showUnitModal = true"
                prependIcon="mdi-plus"
                >Add New</v-btn
              >
              <v-dialog v-model="showUnitModal" width="60rem">
                <unit-modal
                  @uploaded="updateUnits"
                  @close="showUnitModal = false"
                  >Add New</unit-modal
                >
              </v-dialog>
            </v-col>
            <v-col cols="12" md="3">
              <v-autocomplete
                v-model="selectedProcessingLevel"
                label="Select processing level"
                :items="formattedProcessingLevels"
                item-value="id"
                no-data-text="No available processing level"
              ></v-autocomplete>
              <v-btn
                variant="elevated"
                density="comfortable"
                color="green"
                @click="showProcessingLevelModal = true"
                prependIcon="mdi-plus"
                >Add New</v-btn
              >
              <v-dialog v-model="showProcessingLevelModal" width="60rem">
                <processing-level-modal
                  @uploaded="updateProcessingLevels"
                  @close="showProcessingLevelModal = false"
                  >Add New</processing-level-modal
                >
              </v-dialog>
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
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import router from '@/router/router'
import { useApiClient } from '@/utils/api-client'
const api = useApiClient()

const dataStore = useDataStore()
const route = useRoute()
const thingId = route.params.id
const datastreamId = route.params.datastreamId

let selectedDatastream = ref(datastreamId)
const datastreams = ref([])

let selectedUnit = ref('')
let selectedObservedProperty = ref('')
let selectedSensor = ref('')
let selectedProcessingLevel = ref('')

let units = ref([])
let observedProperties = ref([])
let sensors = ref([])
let processingLevels = ref([])

let showSensorModal = ref(false)
let showObservedPropertyModal = ref(false)
let showUnitModal = ref(false)
let showProcessingLevelModal = ref(false)

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

async function updateSensors(newSensorID = null) {
  await dataStore.fetchOrGetFromCache('sensors', '/sensors')
  sensors.value = dataStore.sensors
  if (newSensorID) selectedSensor.value = newSensorID
}

async function updateObservedProperties(newObservedPropertyId = null) {
  await dataStore.fetchOrGetFromCache(
    'observedProperties',
    '/observed-properties'
  )
  observedProperties.value = dataStore.observedProperties
  if (newObservedPropertyId)
    selectedObservedProperty.value = newObservedPropertyId
}

async function updateUnits(newUnitId = null) {
  await dataStore.fetchOrGetFromCache('units', '/units')
  units.value = dataStore.units.sort((a, b) => a.name.localeCompare(b.name))
  if (newUnitId) selectedUnit.value = newUnitId
}

async function updateProcessingLevels(newProcessingLevelId = null) {
  await dataStore.fetchOrGetFromCache('processingLevels', '/processing-levels')
  processingLevels.value = dataStore.processingLevels
  if (newProcessingLevelId) selectedProcessingLevel.value = newProcessingLevelId
}

async function populateDatastream() {
  await dataStore.fetchOrGetFromCache('datastreams', '/datastreams')
  datastreams.value = dataStore.datastreams

  if (selectedDatastream.value) {
    const datastream = datastreams.value.find(
      (ds) => ds.id === selectedDatastream.value
    )
    if (datastream) populateForm(datastream)
  }
}

watch(selectedDatastream, () => populateDatastream())

populateDatastream()
updateSensors()
updateObservedProperties()
updateUnits()
updateProcessingLevels()

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
      await api.put(`/datastreams/${datastreamId}`, payload)
    } else {
      const response = await api.post('/datastreams', payload)
      const newDatastream = response.data
      dataStore.addDatastream(newDatastream)
    }
    localStorage.removeItem(`thing_${thingId}`)
    localStorage.removeItem(`datastreams`)
    await router.push({ name: 'SiteDatastreams', params: { id: thingId } })
  } catch (error) {
    console.log('Error Registering Datastream: ', error)
  }
}
</script>
