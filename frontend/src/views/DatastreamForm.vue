<template>
  <div style="margin: 1rem">
    <h3>Datastream Setup Page</h3>
    <v-form>
      <v-select
        v-model="selectedDatastream"
        :items="datastreams"
        item-text="text"
        item-value="value"
        label="Start from an existing datastream"
      ></v-select>
      <v-btn type="submit">Load Datastream</v-btn>
    </v-form>

    <div>
      <v-form @submit.prevent="loadDatastream">
        <v-container>
          <v-row style="margin-bottom: 1rem">
            <v-col cols="12" md="3">
              <v-select
                v-model="selectedSensor"
                label="Select sensor"
                :items="sensors"
                item-title="name"
                item-value="id"
                no-data-text="No available sensors"
              ></v-select>
              <sensor-modal @sensorCreated="updateSensors"></sensor-modal>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="selectedObservedProperty"
                label="Select observed property"
                :items="observedProperties"
                item-title="name"
                item-value="id"
                no-data-text="No available properties"
              ></v-select>
              <observed-property-modal @observedPropertyCreated="updateObservedProperties">Add New</observed-property-modal>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="selectedUnit"
                label="Select unit"
                :items="units"
                item-title="name"
                item-value="id"
                no-data-text="No available units"
              ></v-select>
              <unit-modal @unitCreated="updateUnits">Add New</unit-modal>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="selectedProcessingLevel"
                label="Select processing level"
                :items="processingLevels"
                item-title="processing_level_code"
                item-value="id"
                no-data-text="No available processing level"
              ></v-select>
              <processing-level-modal @processingLevelCreated="updateProcessingLevels">Add New</processing-level-modal>
            </v-col>
          </v-row>

          <v-text-field
            v-model="ds_name"
            label="Datastream name"
            :rules="[(v) => !!v || 'Name is required']"
            required
          ></v-text-field>
          <v-textarea
            v-model="ds_description"
            label="Datastream description"
            auto-grow
          ></v-textarea>
          <v-text-field
            v-model="ds_sampled_medium"
            label="Sampled medium"
            :rules="[(v) => !!v || 'Sampled medium is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_status"
            label="Status"
            :rules="[(v) => !!v || 'Status is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_no_data_value"
            label="No data value"
            :rules="[(v) => !!v || 'No data value is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_aggregation_statistic"
            label="Aggregation statistic"
            :rules="[(v) => !!v || 'Aggregation statistic is required']"
            required
          ></v-text-field>
          <v-text-field
            v-model="ds_result_type"
            label="Result type"
          ></v-text-field>
          <v-text-field
            v-model="ds_observation_type"
            label="Observation type"
          ></v-text-field>

          <v-btn type="submit" color="green">Save</v-btn>
        </v-container>
      </v-form>
    </div>
  </div>
</template>

<script>
import {ref} from "vue"
import {useDataStore} from "@/store/data.js"
import {useRoute} from "vue-router"
import SensorModal from "@/components/Site/SensorModal.vue";
import ObservedPropertyModal from "@/components/Site/ObservedPropertyModal.vue";
import UnitModal from "@/components/Site/UnitModal.vue";
import ProcessingLevelModal from "@/components/Site/ProcessingLevelModal.vue";
import axios from "@/axiosConfig";
import router from "@/router.js";

export default {
  components: {ProcessingLevelModal, UnitModal, ObservedPropertyModal, SensorModal},
  setup() {
    const dataStore = useDataStore()
    const route = useRoute()
    const thing_id = route.params.id
    let selectedDatastream = ref(null)
    const datastreams = ref([])

    let selectedUnit= ref(null)
    let selectedObservedProperty = ref(null)
    let selectedSensor = ref(null)
    let selectedProcessingLevel = ref(null)

    let units = ref([])
    let observedProperties = ref([])
    let sensors = ref([])
    let processingLevels = ref([])

    const ds_name = ref("");
    const ds_description = ref("");
    const ds_sampled_medium = ref("");
    const ds_status = ref("");
    const ds_no_data_value = ref("");
    const ds_aggregation_statistic = ref("");
    const ds_result_type = ref("");
    const ds_observation_type = ref("");

    async function updateSensors(newSensor) {
      await dataStore.fetchOrGetFromCache('sensors', '/sensors')
      sensors.value = dataStore.sensors
      selectedSensor.value = newSensor
    }

    async function updateObservedProperties(newObservedProperty) {
      await dataStore.fetchOrGetFromCache('observedProperties', '/observed-properties')
      observedProperties.value = dataStore.observedProperties
      selectedObservedProperty.value = newObservedProperty
    }

    async function updateUnits(newUnit) {
      await dataStore.fetchOrGetFromCache('units', '/units')
      units.value = dataStore.units
      selectedUnit.value = newUnit
    }

    async function updateProcessingLevels(newProcessingLevel) {
      await dataStore.fetchOrGetFromCache('processingLevels', '/processing-levels')
      processingLevels.value = dataStore.processingLevels
      selectedProcessingLevel.value = newProcessingLevel
    }

    updateSensors()
    updateObservedProperties()
    updateUnits()
    updateProcessingLevels()

    function waitForValue(valueRef) {
      return new Promise((resolve) => {
        const interval = setInterval(() => {
          if (valueRef.value) {
            clearInterval(interval);
            resolve();
          }
        }, 50);
      });
    }

    async function loadDatastream() {
      await Promise.all([
        waitForValue(selectedSensor),
        waitForValue(selectedObservedProperty),
        waitForValue(selectedUnit),
        waitForValue(selectedProcessingLevel),
      ]);

      // Check if all required data is available
      if (
        selectedSensor.value &&
        selectedObservedProperty.value &&
        selectedUnit.value &&
        selectedProcessingLevel.value
      ) {
        try {
          const response = await axios.post('/datastreams', {
            thing_id,
            name: ds_name.value,
            description: ds_description.value,
            sensor: selectedSensor.value,
            observed_property: selectedObservedProperty.value,
            unit: selectedUnit.value,
            processing_level: selectedProcessingLevel.value,
            sampled_medium: ds_sampled_medium.value,
            status: ds_status.value,
            no_data_value: ds_no_data_value.value,
            aggregation_statistic: ds_aggregation_statistic.value,
            result_type: ds_result_type.value,
            observation_type: ds_observation_type.value,
          });
          localStorage.removeItem(`thing_${thing_id}`);
          await router.push({ name: 'SiteDatastreams', params: { id: thing_id } })
        } catch (error) {
          console.log("Error Registering Datastream: ", error)
        }
      } else {
        console.error("One or more required fields are missing or invalid");
      }
    }

    return {
      observedProperties, selectedObservedProperty, updateObservedProperties,
      sensors, selectedSensor, updateSensors,
      units, selectedUnit, updateUnits,
      processingLevels, selectedProcessingLevel, updateProcessingLevels,
      selectedDatastream, datastreams, loadDatastream,
      ds_name,
      ds_description,
      ds_sampled_medium,
      ds_status,
      ds_no_data_value,
      ds_aggregation_statistic,
      ds_result_type,
      ds_observation_type,}
  },
}
</script>
