<template>
  <v-container v-if="datastream && loaded">
    <v-row>
      <h3>{{ datastreamId ? 'Edit Datastream' : 'Datastream Setup' }} Page</h3>
    </v-row>
    <v-row v-if="thingStore.things[thingId].is_primary_owner">
      <v-col>
        <v-autocomplete
          v-if="!datastreamId"
          v-model="selectedDatastreamID"
          label="Start from an existing datastream"
          :items="formattedDatastream"
          item-value="id"
        ></v-autocomplete>
      </v-col>
    </v-row>

    <v-form @submit.prevent="uploadDatastream">
      <v-row>
        <v-col cols="12" md="3">
          <v-autocomplete
            v-model="datastream.method_id"
            label="Select sensor"
            :items="
              thingStore.things[thingId].is_primary_owner
                ? sensorStore.sensors
                : thingStore.POMetadata[thingId].sensors
            "
            item-title="name"
            item-value="id"
            no-data-text="No available sensors"
          ></v-autocomplete>
          <v-btn
            v-if="thingStore.things[thingId]?.is_primary_owner"
            variant="elevated"
            density="comfortable"
            color="green"
            @click="showSensorModal = true"
            prependIcon="mdi-plus"
            >Add New</v-btn
          >
          <v-dialog
            v-if="thingStore.things[thingId]?.is_primary_owner"
            v-model="showSensorModal"
            width="60rem"
          >
            <sensor-modal
              @uploaded="datastream.method_id = $event"
              @close="showSensorModal = false"
            ></sensor-modal>
          </v-dialog>
        </v-col>
        <v-col cols="12" md="3">
          <v-autocomplete
            v-model="datastream.observed_property_id"
            label="Select observed property"
            :items="
              thingStore.things[thingId].is_primary_owner
                ? opStore.observedProperties
                : thingStore.POMetadata[thingId].observed_properties
            "
            item-title="name"
            item-value="id"
            no-data-text="No available properties"
          ></v-autocomplete>
          <v-dialog
            v-if="thingStore.things[thingId]?.is_primary_owner"
            v-model="showObservedPropertyModal"
            width="60rem"
          >
            <ObservedPropertyModal
              @uploaded="datastream.observed_property_id = $event"
              @close="showObservedPropertyModal = false"
            ></ObservedPropertyModal>
          </v-dialog>
          <v-btn
            v-if="thingStore.things[thingId]?.is_primary_owner"
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
            :items="
              thingStore.things[thingId].is_primary_owner
                ? unitStore.units
                : thingStore.POMetadata[thingId].units
            "
            item-title="name"
            item-value="id"
            no-data-text="No available units"
          ></v-autocomplete>
          <v-btn
            v-if="thingStore.things[thingId]?.is_primary_owner"
            variant="elevated"
            density="comfortable"
            color="green"
            @click="showUnitModal = true"
            prependIcon="mdi-plus"
            >Add New</v-btn
          >
          <v-dialog
            v-if="thingStore.things[thingId]?.is_primary_owner"
            v-model="showUnitModal"
            width="60rem"
          >
            <unit-modal
              @uploaded="datastream.unit_id = $event"
              @close="showUnitModal = false"
              >Add New</unit-modal
            >
          </v-dialog>
        </v-col>
        <v-col cols="12" md="3">
          <v-autocomplete
            v-model="datastream.processing_level_id"
            label="Select processing level"
            :items="
              thingStore.things[thingId].is_primary_owner
                ? plStore.processingLevels
                : thingStore.POMetadata[thingId].processing_levels
            "
            item-title="processing_level_code"
            item-value="id"
            no-data-text="No available processing level"
          ></v-autocomplete>
          <v-btn
            v-if="thingStore.things[thingId]?.is_primary_owner"
            variant="elevated"
            density="comfortable"
            color="green"
            @click="showProcessingLevelModal = true"
            prependIcon="mdi-plus"
            >Add New</v-btn
          >
          <v-dialog
            v-if="thingStore.things[thingId]?.is_primary_owner"
            v-model="showProcessingLevelModal"
            width="60rem"
          >
            <processing-level-modal
              @uploaded="datastream.processing_level_id = $event"
              @close="showProcessingLevelModal = false"
              >Add New</processing-level-modal
            >
          </v-dialog>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            v-model="datastream.sampled_medium"
            label="Sampled medium"
            :rules="[(v) => !!v || 'Sampled medium is required']"
            required
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            v-model="datastream.status"
            label="Status"
            :rules="[(v) => !!v || 'Status is required']"
            required
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            v-model="datastream.no_data_value"
            label="No data value"
            :rules="[(v) => !!v || 'No data value is required']"
            required
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            v-model="datastream.aggregation_statistic"
            label="Aggregation statistic"
            :rules="[(v) => !!v || 'Aggregation statistic is required']"
            required
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            v-model="datastream.result_type"
            label="Result type"
          ></v-text-field>
        </v-col>
        <v-col>
          <v-text-field
            v-model="datastream.observation_type"
            label="Observation type"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-btn type="submit" color="green">{{
        datastreamId ? 'Update' : 'Save'
      }}</v-btn>
    </v-form>
  </v-container>
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
import {
  Datastream,
  ObservedProperty,
  ProcessingLevel,
  Sensor,
  Unit,
} from '@/types'
import { useThingStore } from '@/store/things'

const datastreamStore = useDatastreamStore()
const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const unitStore = useUnitStore()
const plStore = useProcessingLevelStore()
const thingStore = useThingStore()

const route = useRoute()
const thingId = route.params.id.toString()
const datastreamId = route.params.datastreamId?.toString() || ''
const loaded = ref(false)
const selectedDatastreamID = ref(datastreamId)

const showSensorModal = ref(false)
const showObservedPropertyModal = ref(false)
const showUnitModal = ref(false)
const showProcessingLevelModal = ref(false)

const datastream = reactive<Datastream>({
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
  is_primary_owner: false,
})

const formattedDatastream = computed(() => {
  return datastreamStore.primaryOwnedDatastreams.map((datastream) => ({
    id: datastream.id,
    title: `Sensor:${datastream.method_name},  Observed Property: ${datastream.observed_property_name},
     Unit: ${datastream.unit_name},  Processing Level: ${datastream.processing_level_name},
      Sampled Medium ${datastream.sampled_medium}`,
  }))
})

// const formattedProcessingLevels = computed(() => {
//   let processingLevels
//   if (thingStore.things[thingId].is_primary_owner) {
//     processingLevels = plStore.processingLevels
//   } else {
//     processingLevels = thingStore.POMetadata[thingId].processing_levels
//   }
//   return processingLevels.map((pl) => ({
//     id: pl.id,
//     title: `${pl.processing_level_code} : ${pl.definition}`,
//   }))
// })

watch(selectedDatastreamID, async () => {
  await populateForm(selectedDatastreamID.value)
})

async function populateForm(id: string) {
  Object.assign(datastream, await datastreamStore.getDatastreamById(id))
}

async function uploadDatastream() {
  if (datastreamId) await datastreamStore.updateDatastream(datastream)
  else await datastreamStore.createDatastream(datastream)
  await router.push({ name: 'SiteDatastreams', params: { id: thingId } })
}

onMounted(async () => {
  // TODO: fetch all at the same time with Promise.all
  await thingStore.fetchThingById(thingId)
  await datastreamStore.fetchDatastreams()
  await sensorStore.fetchSensors()
  await opStore.fetchObservedProperties()
  await unitStore.fetchUnits()
  await plStore.fetchProcessingLevels()

  if (!thingStore.things[thingId].is_primary_owner) {
    await thingStore.fetchPrimaryOwnerMetadataByThingId(thingId)
  }

  if (datastreamId) await populateForm(datastreamId)
  loaded.value = true
})
</script>
