<template>
  <div class="manage-datastreams" style="margin: 1rem">
    <h1>Manage Site Datastreams</h1>
    <h2>{{ thingName }}</h2>
    <v-btn style="margin-top: .5rem; margin-bottom: 1rem"
           color="primary"
           :to="{name: 'DatastreamForm', params: { id: thing_id } }">Add New Datastream</v-btn>

    <table>
      <thead>
        <tr style="background-color: lightgrey">
          <th>Observed Property</th>
          <th>Method / Sensor</th>
          <th>Units</th>
          <th>Processing Level</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="datastream in datastreams" :key="datastream.id">
          <td>{{ datastream.observed_property }}</td>
          <td>{{ datastream.method }}</td>
          <td>{{ datastream.units }}</td>
          <td>{{ datastream.processing_level }}</td>
          <td>
            <a >Edit</a> |
            <a >Delete</a>
          </td>
        </tr>
      </tbody>
    </table>

    <v-btn color="secondary" :to="{ name: 'SingleSite', params: { id: thing_id } }">Back to Site Details</v-btn>
  </div>
</template>

<script>
import { ref } from 'vue';
import {useRoute} from "vue-router";
import {useDataStore} from "@/store/data.js";

export default {
  setup() {
    const route = useRoute()
    const dataStore = useDataStore()

    const thing_id = route.params.id
    const thingName = ref('')
    const datastreams = ref([])

    let cachedThingName = `thing_${thing_id}`
    dataStore.fetchOrGetFromCache(cachedThingName, `/things/${thing_id}`)
      .then(() => {
        const thing = dataStore[cachedThingName]
        thingName.value = thing.name
        datastreams.value = thing.datastreams
        console.log("thingName: ", thingName.value)
        console.log("datastreams: ", datastreams.value)
      })
      .catch((error) => {console.error("Error fetching thing data from API", error)})

    return {thingName, datastreams, thing_id }
  },
};
</script>

<style scoped>
table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
  border-right: 1px solid lightgray;
  border-bottom: 1px solid lightgray;
  border-collapse: collapse;
  border-spacing: 0;
  margin-left: auto;
  margin-right: auto;
}

table th,
table td {
  padding: 0.1rem;
  vertical-align: middle;
  border-top: 1px solid #dee2e6;
}

table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
}

table tbody + tbody {
  border-top: 2px solid #dee2e6;
}

table th {
  font-weight: 500;
  text-align: left;
}

table tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>