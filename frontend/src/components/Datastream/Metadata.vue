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
    <v-card>
      <v-card-title>
        <span class="text-h5">Confirm Sensor Deletion</span>
      </v-card-title>
      <v-card-text>
        Are you sure you want to delete
        <strong>{{ properties.sensor ? properties.sensor.name : null }}</strong
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
        <v-btn color="red" @click="flags.sensorDelete = false">Cancel</v-btn>
        <v-btn color="green" @click="deleteSensor">Confirm</v-btn>
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
</template>

<script lang="ts" setup>
import ManagerTable from '@/components/ManagerTable.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { useSensorStore } from '@/store/sensors'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useUnitStore } from '@/store/unit'
import { useDatastreamStore } from '@/store/datastreams'
import { ObservedProperty, ProcessingLevel, Sensor, Unit } from '@/types'

const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const plStore = useProcessingLevelStore()
const unitStore = useUnitStore()
const datastreamStore = useDatastreamStore()

let properties = reactive({
  op: null as ObservedProperty | null,
  sensor: null as Sensor | null,
  pl: null as ProcessingLevel | null,
  unit: null as Unit | null,
})

const flags = reactive({
  opModal: ref(false),
  opDelete: ref(false),
  sensorModal: ref(false),
  sensorDelete: ref(false),
  plModal: ref(false),
  plDelete: ref(false),
  unitModal: ref(false),
  unitDelete: ref(false),
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

async function deleteSensor(id: string) {}

const datastreamsForSensor = computed(() => {
  if (properties.sensor) {
    return datastreamStore.getDatastreamsByParameter(
      'method_id',
      properties.sensor.id
    )
  }
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
