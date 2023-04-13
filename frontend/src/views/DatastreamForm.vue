<template>
  <div style="margin: 1rem">
    <h3>Datastream Setup Page</h3>
    <!-- Datastream selection form -->
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
                label="Select"
                :items="['California', 'Colorado', 'Florida', 'Georgia', 'Texas', 'Wyoming']"
              ></v-select>
            <v-btn @click="addMethod">Add New</v-btn>
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
import { ref } from "vue"
import {useDataStore} from "@/store/data.js"
import {useRoute} from "vue-router"

export default {
  setup() {
    const dataStore = useDataStore()
    const selectedDatastream = ref("")
    const datastreams = ref([])
    let methods = ref([])
    let units = ref([])
    let observedProperties = ref([])
    const route = useRoute()
    const thing_id = route.params.id

    let cachedThingName = `thing_${thing_id}`
    dataStore.fetchOrGetFromCache(cachedThingName, `/things/${thing_id}`)
      .then(() => {
        const thing = dataStore[cachedThingName]
        // thingName.value = thing.name
        datastreams.value = thing.datastreams
        // console.log("thingName: ", thingName.value)
        // console.log("datastreams: ", datastreams.value)
      })
      .catch((error) => {console.error("Error fetching thing data from API", error)})

   methods = [
      { id: 1, name: "Method 1" },
      { id: 2, name: "Method 2" },
    ]
    let selectedMethod = null
    observedProperties = [
      { id: 1, name: "Property 1" },
      { id: 2, name: "Property 2" },
    ]
    units = [
      { id: 1, name: "Unit 1" },
      { id: 2, name: "Unit 2" },
    ]

    function loadDatastream() {
      // Load datastream logic
    }

    function saveDatastream() {
      // Save datastream logic
    }

    function addMethod() {
      console.log("Add new method");
    }
    function addObservedProperty() {
      console.log("Add new observed property");
    }
    function addUnit() {
      console.log("Add new unit");
    }

    return {methods,selectedMethod, observedProperties, units, selectedDatastream, datastreams, loadDatastream, saveDatastream , addUnit, addObservedProperty, addMethod}
  },
};
</script>
