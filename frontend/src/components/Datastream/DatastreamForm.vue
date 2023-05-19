<template>
  <div style="margin: 1rem">
    <h3>{{ datastreamId ? 'Edit Datastream' : 'Datastream Setup' }} Page</h3>
    <v-autocomplete
      v-if="!datastreamId"
      v-model="selectedDatastreamID"
      label="Start from an existing datastream"
      :items="formattedDatastream"
      item-value="id"
    ></v-autocomplete>

    <div>
      <v-form @submit.prevent="uploadDatastream">
        <v-container v-if="datastream">
          <v-row style="margin-bottom: 1rem">
            <v-col cols="12" md="3">
              <v-autocomplete
                v-model="datastream.method_id"
                label="Select sensor"
                :items="sensorStore.sensors"
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
                v-model="datastream.observed_property_id"
                label="Select observed property"
                :items="opStore.observedProperties"
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
                v-model="datastream.unit_id"
                label="Select unit"
                :items="unitStore.units"
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
                v-model="datastream.processing_level_id"
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
            v-model="datastream.sampled_medium"
            label="Sampled medium"
            :rules="[(v) => !!v || 'Sampled medium is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="datastream.status"
            label="Status"
            :rules="[(v) => !!v || 'Status is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="datastream.no_data_value"
            label="No data value"
            :rules="[(v) => !!v || 'No data value is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="datastream.aggregation_statistic"
            label="Aggregation statistic"
            :rules="[(v) => !!v || 'Aggregation statistic is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="datastream.result_type"
            label="Result type"
          ></v-text-field>
          <v-text-field
            v-model="datastream.observation_type"
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import router from '@/router/router'
import { useDatastreamStore } from '@/store/datastreams'
import { useSensorStore } from '@/store/sensors'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useUnitStore } from '@/store/unit'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { Datastream } from '@/types'

const datastreamStore = useDatastreamStore()
const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const unitStore = useUnitStore()
const plStore = useProcessingLevelStore()

const route = useRoute()
const thingId = route.params.id.toString()
const datastreamId = route.params.datastreamId?.toString() || ''

let selectedDatastreamID = ref(datastreamId)

let showSensorModal = ref(false)
let showObservedPropertyModal = ref(false)
let showUnitModal = ref(false)
let showProcessingLevelModal = ref(false)

let datastream = reactive<Datastream | null>({
  id: '',
  thing_id: thingId,
  observation_type: '',
  result_type: '',
  status: '',
  sampled_medium: '',
  no_data_value: -999,
  aggregation_statistic: '',
  observations: [],
  most_recent_observation: '',
  unit_id: '',
  unit_name: '',
  observed_property_id: '',
  observed_property_name: '',
  method_id: '',
  method_name: '',
  processing_level_id: '',
  processing_level_name: '',
  is_visible: true,
})

const formattedDatastream = computed(() => {
  return datastreamStore.datastreams[thingId].map((datastream) => ({
    id: datastream.id,
    title: `${datastream.method_name} : ${datastream.observed_property_name} : ${datastream.unit_name} : ${datastream.processing_level_name}`,
  }))
})

const formattedProcessingLevels = computed(() => {
  return plStore.processingLevels.map((pl) => ({
    id: pl.id,
    title: `${pl.processing_level_code} : ${pl.definition}`,
  }))
})

async function updateSensors(id) {
  if (datastream) datastream.method_id = id
}
async function updateObservedProperties(id) {
  if (datastream) datastream.observed_property_id = id
}
async function updateUnits(id) {
  if (datastream) datastream.unit_id = id
}
async function updateProcessingLevels(id) {
  if (datastream) datastream.processing_level_id = id
}

async function populateForm(id: string) {
  if (id) {
    const newDatastream = await datastreamStore.getDatastreamById(thingId, id)

    // This ensures Vue doesn't lose reactivity.
    if (datastream && newDatastream) {
      for (const key in newDatastream) {
        datastream[key] = newDatastream[key]
      }
    }
  }
}

watch(selectedDatastreamID, async () => {
  await populateForm(selectedDatastreamID.value)
})

onMounted(async () => {
  await datastreamStore.fetchDatastreamsByThingId(thingId)
  await sensorStore.fetchSensors()
  await opStore.fetchObservedProperties()
  await unitStore.fetchUnits()
  await plStore.fetchProcessingLevels()
  await populateForm(datastreamId)
})

async function uploadDatastream() {
  try {
    if (datastream) {
      if (datastreamId) await datastreamStore.updateDatastream(datastream)
      else await datastreamStore.createDatastream(datastream)
    }
    await router.push({ name: 'SiteDatastreams', params: { id: thingId } })
  } catch (error) {
    console.log('Error Registering Datastream: ', error)
  }
}
</script>
