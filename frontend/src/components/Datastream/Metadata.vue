<template>
  <h1>Manage Metadata</h1>

  <!--    Sensor Table and Modal-->
  <div class="table-title-container">
    <h2>Sensors</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="handleModal('sensorModal', 'sensor')"
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
      <a @click="handleModal('sensorModal', 'sensor', row)"> Edit </a>
      <span> | </span>
      <a @click="handleModal('sensorDelete', 'sensor', row)">Delete</a>
    </template>
  </ManagerTable>
  <v-dialog v-model="flags.sensorModal" width="60rem">
    <SensorModal
      :id="properties.sensor ? properties.sensor.id : undefined"
      @close="flags.sensorModal = false"
    ></SensorModal>
  </v-dialog>
  <v-dialog v-model="flags.sensorDelete" width="40rem">
    <DeleteModal
      itemName="sensor"
      :item="properties.sensor"
      v-if="properties.sensor"
      parameter-name="method_id"
      @delete="deleteSensor"
      @close="flags.sensorDelete = false"
    ></DeleteModal>
  </v-dialog>

  <!--    Observed Properties Table and Modal-->
  <div class="table-title-container">
    <h2>Observed Properties</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="handleModal('opModal', 'op')"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="OPNameMappings" :rows="opStore.observedProperties">
    <template v-slot:actions="{ row }">
      <a @click="handleModal('opModal', 'op', row)"> Edit </a>
      <span> | </span>
      <a @click="handleModal('opDelete', 'op', row)">Delete</a>
    </template>
  </ManagerTable>
  <v-dialog v-model="flags.opModal" width="60rem">
    <ObservedPropertyModal
      :observedProperty="properties.op"
      :id="properties.op ? properties.op.id : undefined"
      @close="flags.opModal = false"
    ></ObservedPropertyModal>
  </v-dialog>
  <v-dialog v-model="flags.opDelete" width="40rem">
    <DeleteModal
      itemName="Observed Property"
      :item="properties.op"
      v-if="properties.op"
      parameter-name="observed_property_id"
      @delete="deleteObservedProperty"
      @close="flags.opDelete = false"
    ></DeleteModal>
  </v-dialog>

  <!--    Processing Levels Table and Modal-->
  <div class="table-title-container">
    <h2>Processing Levels</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="handleModal('plModal', 'pl')"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable
    :names="ProcLevelNameMappings"
    :rows="plStore.ownedProcessingLevels"
  >
    <template v-slot:actions="{ row }">
      <a @click="handleModal('plModal', 'pl', row)"> Edit </a>
      <span> | </span>
      <a @click="handleModal('plDelete', 'pl', row)">Delete</a>
    </template></ManagerTable
  >
  <v-dialog v-model="flags.plModal" width="60rem">
    <ProcessingLevelModal
      :id="properties.pl ? String(properties.pl.id) : undefined"
      @close="flags.plModal = false"
    ></ProcessingLevelModal>
  </v-dialog>
  <v-dialog v-model="flags.plDelete" width="40rem">
    <DeleteModal
      itemName="processing level"
      :item="properties.pl"
      v-if="properties.pl"
      parameter-name="processing_level_id"
      @delete="deleteProcessingLevel"
      @close="flags.plDelete = false"
    ></DeleteModal>
  </v-dialog>

  <!--    Units Table and Modal-->
  <div class="table-title-container">
    <h2>Units</h2>
    <v-btn
      variant="elevated"
      density="comfortable"
      color="green"
      @click="handleModal('unitModal', 'unit')"
      prependIcon="mdi-plus"
      >Add New</v-btn
    >
  </div>
  <ManagerTable :names="UnitNameMappings" :rows="unitStore.ownedUnits">
    <template v-slot:actions="{ row }">
      <a @click="handleModal('unitModal', 'unit', row)"> Edit </a>
      <span> | </span>
      <a @click="handleModal('unitDelete', 'unit', row)">Delete</a>
    </template></ManagerTable
  >
  <v-dialog v-model="flags.unitModal" width="60rem">
    <UnitModal
      :id="properties.unit ? String(properties.unit.id) : undefined"
      @close="flags.unitModal = false"
    ></UnitModal>
  </v-dialog>
  <v-dialog v-model="flags.unitDelete" width="40rem">
    <DeleteModal
      itemName="unit"
      :item="properties.unit"
      v-if="properties.unit"
      parameter-name="unit_id"
      @delete="deleteUnit"
      @close="flags.unitDelete = false"
    ></DeleteModal>
  </v-dialog>
</template>

<script lang="ts" setup>
import ManagerTable from '@/components/ManagerTable.vue'
import { onMounted, reactive, ref } from 'vue'
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { useSensorStore } from '@/store/sensors'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useUnitStore } from '@/store/unit'
import { ObservedProperty, ProcessingLevel, Sensor, Unit } from '@/types'
import DeleteModal from '@/components/Datastream/deleteModal.vue'

const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const plStore = useProcessingLevelStore()
const unitStore = useUnitStore()

const properties: {
  op: ObservedProperty | null
  sensor: Sensor | null
  pl: ProcessingLevel | null
  unit: Unit | null
  [key: string]: any
} = reactive({
  op: null,
  sensor: null,
  pl: null,
  unit: null,
})

const flags: {
  [key: string]: boolean
} = reactive({
  opModal: false,
  opDelete: false,
  sensorModal: false,
  sensorDelete: false,
  plModal: false,
  plDelete: false,
  unitModal: false,
  unitDelete: false,
})

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

function handleModal(
  flagKey: string,
  propertyKey: string,
  property = null as any
) {
  properties[propertyKey] = property
  flags[flagKey] = true
}

async function deleteSensor() {
  flags.sensorDelete = false
  if (properties.sensor) await sensorStore.deleteSensor(properties.sensor.id)
}

async function deleteObservedProperty() {
  flags.opDelete = false
  if (properties.op) await opStore.deleteObservedProperty(properties.op.id)
}

async function deleteProcessingLevel() {
  flags.plDelete = false
  if (properties.pl) await plStore.deleteProcessingLevel(properties.pl.id)
}

async function deleteUnit() {
  flags.unitDelete = false
  if (properties.unit) await unitStore.deleteUnit(properties.unit.id)
}

onMounted(() => {
  sensorStore.fetchSensors()
  opStore.fetchObservedProperties()
  plStore.fetchProcessingLevels()
  unitStore.fetchUnits()
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
