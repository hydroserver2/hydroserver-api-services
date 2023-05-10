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
  <ManagerTable :names="sensorNameMappings" :rows="sensors">
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
      <a @click="">Delete</a>
    </template>
  </ManagerTable>
  <v-dialog v-model="showSensorModal" width="60rem">
    <SensorModal
      :sensor="selectedProperty"
      @close="showSensorModal = false"
      @uploaded="updateSensors"
    ></SensorModal>
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
  <ManagerTable :names="OPNameMappings" :rows="observedProperties">
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
      @uploaded="updateObservedProperties"
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
  <ManagerTable :names="ProcLevelNameMappings" :rows="ownedProcessingLevels">
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
      @uploaded="updateProcessingLevels"
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
  <ManagerTable :names="UnitNameMappings" :rows="ownedUnits">
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
      @uploaded="updateUnits"
    ></UnitModal>
  </v-dialog>
</template>

<script lang="ts" setup>
import ManagerTable from '@/components/ManagerTable.vue'
import { computed, onMounted, Ref, ref } from 'vue'
import { useDataStore } from '@/store/data'
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'

const showObservedPropertyModal = ref(false)
const showSensorModal = ref(false)
const showProcessingLevelModal = ref(false)
const showUnitModal = ref(false)

type NameTuple = [string, string]

const sensorNameMappings = ref<NameTuple[]>([
  ['id', 'UUID'],
  ['method_type', 'Method Type'],
  ['name', 'Name'],
  ['method_code', 'Method Code'],
])

// For Observed Properties Table
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

let observedProperties = ref([])
let sensors = ref([])
let processingLevels = ref([])
let units = ref([])

let selectedProperty = ref(null)

const ownedProcessingLevels = computed(() => {
  if (processingLevels.value.length === 0) return []
  return processingLevels.value.filter(
    (processingLevel) => processingLevel.person !== null
  )
})

const ownedUnits = computed(() => {
  if (units.value.length === 0) return []
  return units.value.filter((unit) => unit.person !== null)
})

const dataStore = useDataStore()
async function fetchStateData<T>(
  cacheKey: string,
  url: string,
  dataRef: Ref<T[]>
): Promise<void> {
  await dataStore.fetchOrGetFromCache(cacheKey, url)
  dataRef.value = dataStore[cacheKey] as T[]
}

async function updateSensors() {
  await dataStore.fetchOrGetFromCache('sensors', '/sensors')
  sensors.value = dataStore.sensors
}

async function updateObservedProperties() {
  await dataStore.fetchOrGetFromCache(
    'observedProperties',
    '/observed-properties'
  )
  observedProperties.value = dataStore.observedProperties
}

async function updateUnits() {
  await dataStore.fetchOrGetFromCache('units', '/units')
  units.value = dataStore.units
}

async function updateProcessingLevels() {
  await dataStore.fetchOrGetFromCache('processingLevels', '/processing-levels')
  processingLevels.value = dataStore.processingLevels
}

onMounted(() => {
  updateSensors()
  updateObservedProperties()
  updateUnits()
  updateProcessingLevels()
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
