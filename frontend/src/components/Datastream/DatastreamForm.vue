<template>
  <v-container v-if="datastream">
    <v-row>
      <h3>{{ datastreamId ? 'Edit Datastream' : 'Datastream Setup' }} Page</h3>
    </v-row>
    <v-row>
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
              @uploaded="datastream.method_id = $event"
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
              @uploaded="datastream.observed_property_id = $event"
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
import { Datastream } from '@/types'

const datastreamStore = useDatastreamStore()
const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const unitStore = useUnitStore()
const plStore = useProcessingLevelStore()

const route = useRoute()
const thingId = route.params.id.toString()
const datastreamId = route.params.datastreamId?.toString() || ''

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

watch(selectedDatastreamID, async () => {
  await populateForm(selectedDatastreamID.value)
})

async function populateForm(id: string) {
  Object.assign(
    datastream,
    await datastreamStore.getDatastreamById(thingId, id)
  )
}

async function uploadDatastream() {
  if (datastreamId) await datastreamStore.updateDatastream(datastream)
  else await datastreamStore.createDatastream(datastream)
  await router.push({ name: 'SiteDatastreams', params: { id: thingId } })
}

onMounted(async () => {
  // TODO: fetch all at the same time with Promise.all
  await datastreamStore.fetchDatastreamsByThingId(thingId)
  await sensorStore.fetchSensors()
  await opStore.fetchObservedProperties()
  await unitStore.fetchUnits()
  await plStore.fetchProcessingLevels()
  if (datastreamId) await populateForm(datastreamId)
})
</script>
