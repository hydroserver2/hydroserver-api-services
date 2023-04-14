<template>
  <div style="margin: 1rem">
    <h3>Datastream Setup Page</h3>
    <v-form @submit.prevent="loadDatastream">
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
      <v-form>
        <v-container>
          <v-row>
            <v-col cols="12" md="4">
                  <v-select
                    v-model="selectedSensor"
                    label="Select sensor"
                    :items="sensorNames"
                    no-data-text="No available sensors"
                  ></v-select>
                <sensor-modal @sensorCreated="updateSensors"></sensor-modal>
            </v-col>
  <!--          <v-col cols="12" md="4">-->
  <!--            <v-select-->
  <!--              :items="observedProperties"-->
  <!--              item-text="name"-->
  <!--              item-value="id"-->
  <!--              return-object-->
  <!--              placeholder="Please select a property"-->
  <!--            ></v-select>-->
  <!--            <v-btn @click="addObservedProperty">Add New</v-btn>-->
  <!--          </v-col>-->
  <!--          <v-col cols="12" md="4">-->
  <!--            <v-select-->
  <!--              :items="units"-->
  <!--              item-text="name"-->
  <!--              item-value="id"-->
  <!--              return-object-->
  <!--              placeholder="Please select a unit"-->
  <!--            ></v-select>-->
  <!--            <v-btn @click="addUnit">Add New</v-btn>-->
  <!--          </v-col>-->
          </v-row>
          <v-btn type="submit" color="green">Save</v-btn>
        </v-container>
      </v-form>
    </div>
  </div>
</template>

<script>
import {computed, ref} from "vue"
import {useDataStore} from "@/store/data.js"
import {useRoute} from "vue-router"
import SensorModal from "@/components/Site/SensorModal.vue";

export default {
  components: {SensorModal},
  setup() {
    const dataStore = useDataStore()
    const route = useRoute()
    const thing_id = route.params.id

    const selectedDatastream = ref("")
    const datastreams = ref([])
    let units = ref([])
    let observedProperties = ref([])
    let sensors = ref([])
    let selectedSensor = ref(null)
    console.log("hello")

    const sensorNames = computed(() => sensors.value.map(sensor => sensor.name));

    function loadDatastream() { }

    async function updateSensors(newSensorName) {
      await dataStore.fetchOrGetFromCache('sensors', '/sensors')
      sensors.value = dataStore.sensors;
      selectedSensor.value = newSensorName
    }

    updateSensors()

    return {sensorNames, selectedSensor, updateSensors, sensors, observedProperties,
      units, selectedDatastream, datastreams, loadDatastream}
  },
}
</script>
