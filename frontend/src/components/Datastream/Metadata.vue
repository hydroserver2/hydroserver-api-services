<template>
  <v-container>
    <h4 class="text-h4 mb-4">Manage Metadata</h4>

    <!--    Sensor Table and Modal-->
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Sensors</h5>
      </v-col>
      <v-col>
        <v-btn-add @click="openSensorDialog()">Add New</v-btn-add>
      </v-col>
    </v-row>
    <v-data-table
      :headers="sensorHeaders"
      :items="sensorStore.sensors"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon @click="openSensorDialog(item.raw)"> mdi-pencil </v-icon>
        <v-icon @click="openSensorDeleteDialog(item.raw)"> mdi-delete </v-icon>
      </template></v-data-table
    >
    <v-dialog v-model="isSensorCEModalOpen" width="60rem">
      <SensorModal
        :id="isSensorSelected ? selectedSensor.id : undefined"
        @close="isSensorCEModalOpen = false"
      ></SensorModal>
    </v-dialog>
    <v-dialog v-model="isSensorDModalOpen" width="40rem">
      <DeleteModal
        itemName="sensor"
        :itemID="selectedSensor.id"
        parameter-name="method_id"
        @delete="deleteSensor"
        @close="isSensorDModalOpen = false"
      ></DeleteModal>
    </v-dialog>

    <!--    Observed Properties Table and Modal-->
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Observed Properties</h5>
      </v-col>
      <v-col>
        <v-btn-add @click="openOPDialog()">Add New</v-btn-add>
      </v-col>
    </v-row>
    <v-data-table
      :headers="OPHeaders"
      :items="opStore.observedProperties"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon @click="openOPDialog(item.raw)"> mdi-pencil </v-icon>
        <v-icon @click="openOPDeleteDialog(item.raw)"> mdi-delete </v-icon>
      </template></v-data-table
    >
    <v-dialog v-model="isOPCEModalOpen" width="60rem">
      <ObservedPropertyModal
        :id="isOPSelected ? selectedOP.id : null"
        @close="isOPCEModalOpen = false"
      ></ObservedPropertyModal>
    </v-dialog>
    <v-dialog v-model="isOPDModalOpen" width="40rem">
      <DeleteModal
        itemName="Observed Property"
        :itemID="selectedOP.id"
        parameter-name="observed_property_id"
        @delete="deleteOP"
        @close="isOPDModalOpen = false"
      ></DeleteModal>
    </v-dialog>

    <!--    Processing Levels Table and Modal-->
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Processing Levels</h5>
      </v-col>
      <v-col>
        <v-btn-add @click="openPLDialog()">Add New</v-btn-add>
      </v-col>
    </v-row>
    <v-data-table
      :headers="ProcLevelHeaders"
      :items="plStore.ownedProcessingLevels"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon @click="openPLDialog(item.raw)"> mdi-pencil </v-icon>
        <v-icon @click="openPLDeleteDialog(item.raw)"> mdi-delete </v-icon>
      </template></v-data-table
    >
    <v-dialog v-model="isPLCEModalOpen" width="60rem">
      <ProcessingLevelModal
        :id="isPLSelected ? selectedPL.id : undefined"
        @close="isPLCEModalOpen = false"
      ></ProcessingLevelModal>
    </v-dialog>
    <v-dialog v-model="isPLDModalOpen" width="40rem">
      <DeleteModal
        itemName="processing level"
        :itemID="selectedPL.id"
        parameter-name="processing_level_id"
        @delete="deletePL"
        @close="isPLDModalOpen = false"
      ></DeleteModal>
    </v-dialog>

    <!--    Units Table and Modal-->
    <v-row class="justify-start pt-5 pb-2">
      <v-col cols="auto">
        <h5 class="text-h5">Units</h5>
      </v-col>
      <v-col>
        <v-btn-add @click="openUnitDialog()">Add New</v-btn-add>
      </v-col>
    </v-row>
    <v-data-table
      :headers="UnitHeaders"
      :items="unitStore.ownedUnits"
      class="elevation-3"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon @click="openUnitDialog(item.raw)"> mdi-pencil </v-icon>
        <v-icon @click="openUnitDeleteDialog(item.raw)"> mdi-delete </v-icon>
      </template></v-data-table
    >
    <v-dialog v-model="isUnitCEModalOpen" width="60rem">
      <UnitModal
        :id="isUnitSelected ? selectedUnit.id : undefined"
        @close="isUnitCEModalOpen = false"
      ></UnitModal>
    </v-dialog>
    <v-dialog v-model="isUnitDModalOpen" width="40rem">
      <DeleteModal
        itemName="unit"
        :itemID="selectedUnit.id"
        parameter-name="unit_id"
        @delete="deleteUnit"
        @close="isUnitDModalOpen = false"
      ></DeleteModal>
    </v-dialog>
  </v-container>
</template>

<script lang="ts" setup>
import SensorModal from '@/components/Datastream/SensorModal.vue'
import ObservedPropertyModal from '@/components/Datastream/ObservedPropertyModal.vue'
import ProcessingLevelModal from '@/components/Datastream/ProcessingLevelModal.vue'
import UnitModal from '@/components/Datastream/UnitModal.vue'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { useSensorStore } from '@/store/sensors'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useUnitStore } from '@/store/unit'
import DeleteModal from '@/components/Datastream/deleteModal.vue'
import {
  useSensors,
  useUnits,
  useProcessingLevels,
  useObservedProperties,
} from '@/composables/useMetadata'

const sensorStore = useSensorStore()
const opStore = useObservedPropertyStore()
const plStore = useProcessingLevelStore()
const unitStore = useUnitStore()

const {
  isEntitySelected: isSensorSelected,
  selectedEntity: selectedSensor,
  deleteSelectedEntity: deleteSensor,
  isCreateEditModalOpen: isSensorCEModalOpen,
  isDeleteModalOpen: isSensorDModalOpen,
  openDialog: openSensorDialog,
  openDeleteDialog: openSensorDeleteDialog,
} = useSensors()

const {
  isEntitySelected: isUnitSelected,
  selectedEntity: selectedUnit,
  deleteSelectedEntity: deleteUnit,
  isCreateEditModalOpen: isUnitCEModalOpen,
  isDeleteModalOpen: isUnitDModalOpen,
  openDialog: openUnitDialog,
  openDeleteDialog: openUnitDeleteDialog,
} = useUnits()

const {
  isEntitySelected: isPLSelected,
  selectedEntity: selectedPL,
  deleteSelectedEntity: deletePL,
  isCreateEditModalOpen: isPLCEModalOpen,
  isDeleteModalOpen: isPLDModalOpen,
  openDialog: openPLDialog,
  openDeleteDialog: openPLDeleteDialog,
} = useProcessingLevels()

const {
  isEntitySelected: isOPSelected,
  selectedEntity: selectedOP,
  deleteSelectedEntity: deleteOP,
  isCreateEditModalOpen: isOPCEModalOpen,
  isDeleteModalOpen: isOPDModalOpen,
  openDialog: openOPDialog,
  openDeleteDialog: openOPDeleteDialog,
} = useObservedProperties()

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
</script>

<style scoped>
.v-icon {
  color: rgb(var(--v-theme-cancel));
}
</style>
