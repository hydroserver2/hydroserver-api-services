<template>
  <h1>Manage Metadata</h1>

  <!--    Sensor Table and Modal-->
  <div class="table-title-container">
    <h2>Sensors</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="
        () => {
          selectedProperty = null
          showSensorModal = true
        }
      "
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>

  <!--  <v-data-table-->
  <!--    v-if="sensorStore.sensors.length"-->
  <!--    :headers="sensorHeaders"-->
  <!--    :items="sensorStore.sensors"-->
  <!--    hover-->
  <!--    item-value="id"-->
  <!--    class="elevation-1"-->
  <!--  ></v-data-table>-->
  <ManagerTable :names="sensorNameMappings" :rows="sensorStore.sensors">
    <template v-slot:actions="{ row }">
      <a
        @click="
          () => {
            selectedProperty = row
            showSensorModal = true
          }
        "
      >
        Edit
      </a>
      <span> | </span>
      <a
        @click="
          () => {
            selectedProperty = row
            showSensorDeleteModal = true
          }
        "
        >Delete</a
      >
    </template>
  </ManagerTable>
  <v-dialog v-model="showSensorModal" width="60rem">
    <SensorModal
      :sensor="selectedProperty"
      @close="showSensorModal = false"
    ></SensorModal>
  </v-dialog>
  <v-dialog
    v-if="selectedProperty"
    v-model="showSensorDeleteModal"
    width="40rem"
  >
    <v-card>
      <v-card-title>
        <span class="text-h5">Confirm Sensor Deletion</span>
      </v-card-title>
      <v-card-text>
        Are you sure you want to delete
        <strong>{{ selectedProperty.name }}</strong
        >?
        <br />
        <br />
        <div v-if="datastreamsForSensor.length > 0">
          This action will not only delete the sensor method, but will delete
          all datastreams that use this method and all the observations that
          belong to those datastreams. The datastreams that will be deleted with
          this sensor are:
          <br />
          <div v-for="datastream in datastreamsForSensor" :key="datastream.id">
            <br />
            DatastreamID: {{ datastream.id }} <br />
            Observed Property:
            {{ datastream.observed_property_name }}<br />
            Unit:
            {{ datastream.unit_name }}
            <br />
          </div>
        </div>
        <div v-else>
          This sensor method isn't being used by any datastreams and is safe to
          delete
        </div>
        <br />
      </v-card-text>
      <v-card-actions>
        <v-btn color="red" @click="showSensorDeleteModal = false">Cancel</v-btn>
        <v-btn color="green" @click="deleteSensor()">Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!--    Observed Properties Table and Modal-->
  <div class="table-title-container">
    <h2>Observed Properties</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="
        () => {
          selectedProperty = null
          showObservedPropertyModal = true
        }
      "
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="OPNameMappings" :rows="opStore.observedProperties">
    <template v-slot:actions="{ row }">
      <a
        @click="
          () => {
            selectedProperty = row
            showObservedPropertyModal = true
          }
        "
      >
        Edit
      </a>
      <span> | </span>
      <a @click="">Delete</a>
    </template>
  </ManagerTable>
  <v-dialog v-model="showObservedPropertyModal" width="60rem">
    <ObservedPropertyModal
      :observedProperty="selectedProperty"
      @close="showObservedPropertyModal = false"
    ></ObservedPropertyModal>
  </v-dialog>

  <!--    Processing Levels Table and Modal-->
  <div class="table-title-container">
    <h2>Processing Levels</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="
        () => {
          selectedProperty = null
          showProcessingLevelModal = true
        }
      "
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable
    :names="ProcLevelNameMappings"
    :rows="plStore.ownedProcessingLevels"
  >
    <template v-slot:actions="{ row }">
      <a
        @click="
          () => {
            selectedProperty = row
            showProcessingLevelModal = true
          }
        "
      >
        Edit
      </a>
      <span> | </span>
      <a @click="">Delete</a>
    </template></ManagerTable
  >
  <v-dialog v-model="showProcessingLevelModal" width="60rem">
    <ProcessingLevelModal
      :processingLevel="selectedProperty"
      @close="showProcessingLevelModal = false"
    ></ProcessingLevelModal>
  </v-dialog>

  <!--    Units Table and Modal-->
  <div class="table-title-container">
    <h2>Units</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="
        () => {
          selectedProperty = null
          showUnitModal = true
        }
      "
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="UnitNameMappings" :rows="unitStore.ownedUnits">
    <template v-slot:actions="{ row }">
      <a
        @click="
          () => {
            selectedProperty = row
            showUnitModal = true
          }
        "
      >
        Edit
      </a>
      <span> | </span>
      <a @click="">Delete</a>
    </template></ManagerTable
  >
  <v-dialog v-model="showUnitModal" width="60rem">
    <UnitModal
      :unit="selectedProperty"
      @close="showUnitModal = false"
    ></UnitModal>
  </v-dialog>
</template>

<script lang="ts" setup>
import ManagerTable from '@/components/ManagerTable.vue'
import { computed, onMounted, ref } from 'vue'
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { useSensorStore } from '@/store/sensors'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useUnitStore } from '@/store/unit'
import { useDatastreamStore } from '@/store/datastreams'

const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const plStore = useProcessingLevelStore()
const unitStore = useUnitStore()
const datastreamStore = useDatastreamStore()

const showObservedPropertyModal = ref(false)
const showSensorModal = ref(false)
const showProcessingLevelModal = ref(false)
const showUnitModal = ref(false)

const showObservedPropertyDeleteModal = ref(false)
const showSensorDeleteModal = ref(false)
const showProcessingLevelDeleteModal = ref(false)
const showUnitDeleteModal = ref(false)

type NameTuple = [string, string]

const sensorNameMappings = ref<NameTuple[]>([
  ['id', 'UUID'],
  ['method_type', 'Method Type'],
  ['name', 'Name'],
  ['method_code', 'Method Code'],
])

// const sensorHeaders = [
//   {
//     title: 'UUID',
//     align: 'start',
//     sortable: true,
//     key: 'id',
//   },
//   {
//     title: 'Method Type',
//     align: 'start',
//     sortable: true,
//     key: 'method_type',
//   },
//   {
//     title: 'Name',
//     align: 'start',
//     sortable: true,
//     key: 'name',
//   },
//   {
//     title: 'Method Code',
//     align: 'start',
//     sortable: true,
//     key: 'method_code',
//   },
// ]

const OPNameMappings = ref<NameTuple[]>([
  ['name', 'Name'],
  ['variable_type', 'Variable Type'],
  ['variable_code', 'Variable Code'],
])

const ProcLevelNameMappings = ref<NameTuple[]>([
  ['processing_level_code', 'Processing Level Code'],
  ['definition', 'Definition'],
  ['explanation', 'Explanation'],
])

const UnitNameMappings = ref<NameTuple[]>([
  ['name', 'Name'],
  ['symbol', 'Symbol'],
  ['unit_type', 'Unit Type'],
])

let selectedProperty = ref(null)

async function deleteSensor(id: string) {
  showSensorDeleteModal.value = false
  // sensorStore.deleteSensor()
}

const datastreamsForSensor = computed(() => {
  return datastreamStore.getDatastreamsByParameter(
    'method_id',
    selectedProperty.value.id
  )
})

onMounted(() => {
  sensorStore.fetchSensors()
  opStore.fetchObservedProperties()
  plStore.fetchProcessingLevels()
  unitStore.fetchUnits()
  datastreamStore.fetchDatastreams()
})
</script>

<style scoped>
.table-title-container {
  display: flex;
  align-items: center;
  justify-content: left;
  margin-bottom: 1rem;
}
</style>
