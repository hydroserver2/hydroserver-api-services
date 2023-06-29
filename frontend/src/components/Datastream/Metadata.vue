<template>
  <v-container>
    <h4 class="text-h4 mb-4">Manage Metadata</h4>

    <!--    Sensor Table and Modal-->
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Sensors</h5>
      </v-col>
      <v-col>
        <v-btn-secondary
          variant="elevated"
          @click="handleModal('sensorModal', 'sensor')"
          prependIcon="mdi-plus"
          >Add New</v-btn-secondary
        >
      </v-col>
    </v-row>
    <v-data-table
      v-if="sensorStore.sensors.length"
      :headers="sensorHeaders"
      :items="sensorStore.sensors"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon
          small
          color="grey"
          @click="handleModal('sensorModal', 'sensor', item.raw)"
        >
          mdi-pencil
        </v-icon>
        <v-icon
          small
          color="grey"
          @click="handleModal('sensorDelete', 'sensor', item.raw)"
        >
          mdi-delete
        </v-icon>
      </template></v-data-table
    >
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
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Observed Properties</h5>
      </v-col>
      <v-col>
        <v-btn-secondary
          variant="elevated"
          @click="handleModal('opModal', 'op')"
          prependIcon="mdi-plus"
          >Add New</v-btn-secondary
        >
      </v-col>
    </v-row>
    <v-data-table
      :headers="OPHeaders"
      :items="opStore.observedProperties"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon
          small
          color="grey"
          @click="handleModal('opModal', 'op', item.raw)"
        >
          mdi-pencil
        </v-icon>
        <v-icon
          small
          color="grey"
          @click="handleModal('opDelete', 'op', item.raw)"
        >
          mdi-delete
        </v-icon>
      </template></v-data-table
    >
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
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Processing Levels</h5>
      </v-col>
      <v-col>
        <v-btn-secondary
          variant="elevated"
          @click="handleModal('plModal', 'pl')"
          prependIcon="mdi-plus"
          >Add New</v-btn-secondary
        >
      </v-col>
    </v-row>
    <v-data-table
      :headers="ProcLevelHeaders"
      :items="plStore.ownedProcessingLevels"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon
          small
          color="grey"
          @click="handleModal('plModal', 'pl', item.raw)"
        >
          mdi-pencil
        </v-icon>
        <v-icon
          small
          color="grey"
          @click="handleModal('plDelete', 'pl', item.raw)"
        >
          mdi-delete
        </v-icon>
      </template></v-data-table
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
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Units</h5>
      </v-col>
      <v-col>
        <v-btn-secondary
          variant="elevated"
          @click="handleModal('unitModal', 'unit')"
          prependIcon="mdi-plus"
          >Add New</v-btn-secondary
        >
      </v-col>
    </v-row>
    <v-data-table
      :headers="UnitHeaders"
      :items="unitStore.ownedUnits"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon
          small
          color="grey"
          @click="handleModal('unitModal', 'unit', item.raw)"
        >
          mdi-pencil
        </v-icon>
        <v-icon
          small
          color="grey"
          @click="handleModal('unitDelete', 'unit', item.raw)"
        >
          mdi-delete
        </v-icon>
      </template></v-data-table
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
  </v-container>
</template>

<script lang="ts" setup>
import { onMounted, reactive } from 'vue'
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

const sensorHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Method Type', key: 'method_type' },
  { title: 'Method Code', key: 'method_code' },
  { title: 'UUID', key: 'id' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
]

const OPHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Variable Type', key: 'variable_type' },
  { title: 'Variable Code', key: 'variable_code' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
]

const ProcLevelHeaders = [
  { title: 'Processing Level Code', key: 'processing_level_code' },
  { title: 'Definition', key: 'definition' },
  { title: 'Explanation', key: 'explanation' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
]

const UnitHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Unit Type', key: 'unit_type' },
  { title: 'Symbol', key: 'symbol' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
]

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

onMounted(async () => {
  await Promise.all([
    sensorStore.fetchSensors(),
    opStore.fetchObservedProperties(),
    plStore.fetchProcessingLevels(),
    unitStore.fetchUnits(),
  ])
})
</script>
