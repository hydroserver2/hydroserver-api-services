<template>
  <h1>Manage Metadata</h1>
  <div class="table-title-container">
    <h2>Sensors</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="showSensorModal = true"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="sensorNameMappings" :rows="sensors">
    <template v-slot:actions="{ row }">
      <router-link to="/home"> Edit </router-link>
      <span> | </span>
      <a @click="">Delete</a>
    </template>
  </ManagerTable>

  <div class="table-title-container">
    <h2>Observed Properties</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="showObservedPropertyModal = true"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="OPNameMappings" :rows="observedProperties">
    <template v-slot:actions="{ row }">
      <router-link to="/home"> Edit </router-link>
      <span> | </span>
      <a @click="">Delete</a>
    </template>
  </ManagerTable>

  <div class="table-title-container">
    <h2>Processing Levels</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="showProcessingLevelModal = true"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="ProcLevelNameMappings" :rows="ownedProcessingLevels">
    <template v-slot:actions="{ row }">
      <router-link to="/home"> Edit </router-link>
      <span> | </span>
      <a @click="">Delete</a>
    </template></ManagerTable
  >

  <div class="table-title-container">
    <h2>Units</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="showUnitModal = true"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="UnitNameMappings" :rows="ownedUnits">
    <template v-slot:actions="{ row }">
      <router-link to="/home"> Edit </router-link>
      <span> | </span>
      <a @click="">Delete</a>
    </template></ManagerTable
  >

  <v-dialog v-model="showSensorModal" width="60rem">
    <SensorModal
      @close="showSensorModal = false"
      @siteCreated="fetchStateData('sensors', '/sensors', sensors)"
    ></SensorModal>
  </v-dialog>
</template>

<script lang="ts" setup>
import ManagerTable from '@/components/ManagerTable.vue'
import { computed, Ref, ref } from 'vue'
import { useDataStore } from '@/store/data'
import SensorModal from '@/components/Site/SensorModal.vue'

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
  console.log(cacheKey, dataRef.value)
}

fetchStateData('sensors', '/sensors', sensors)
fetchStateData('observedProperties', '/observed-properties', observedProperties)
fetchStateData('units', '/units', units)
fetchStateData('processingLevels', '/processing-levels', processingLevels)
</script>

<style scoped>
.table-title-container {
  display: flex;
  align-items: center;
  justify-content: left;
  margin-bottom: 1rem;
}
</style>
