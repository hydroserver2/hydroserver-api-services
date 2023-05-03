<template>
  <div class="manage-datastreams" style="margin: 1rem">
    <h1>Manage Site Datastreams</h1>
    <h2>{{ thingName }}</h2>
    <v-btn
      style="margin-top: 0.5rem; margin-bottom: 1rem"
      color="primary"
      :to="{ name: 'DatastreamForm', params: { id: thing_id } }"
      >Add New Datastream</v-btn
    >

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
          <td>{{ datastream.observed_property_name }}</td>
          <td>{{ datastream.method_name }}</td>
          <td>{{ datastream.unit_name }}</td>
          <td>{{ datastream.processing_level_name }}</td>
          <td>
            <router-link
              class="action-link"
              :to="{
                name: 'DatastreamForm',
                params: { id: thing_id, datastreamId: datastream.id },
              }"
              >Edit
            </router-link>
            <span class="action-link-separator"> | </span>
            <a class="action-link" @click="showModal(datastream)">Delete</a>
          </td>
        </tr>
      </tbody>
    </table>
    <delete-datastream-modal
      v-if="selectedDatastream"
      :thing-id="thing_id"
      :datastream-id="selectedDatastream.id"
      :datastream-observed-property="selectedDatastream.observed_property_name"
      :datastream-method="selectedDatastream.method_name"
      :datastream-processing-level="selectedDatastream.processing_level_name"
      v-model="showDeleteModal"
      @close="showDeleteModal = false"
      @deleted="onDatastreamDeleted"
    ></delete-datastream-modal>

    <v-btn
      color="secondary"
      :to="{ name: 'SingleSite', params: { id: thing_id } }"
      >Back to Site Details</v-btn
    >
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/store/data'
import DeleteDatastreamModal from '@/components/Site/DeleteDatastreamModal.vue'

const route = useRoute()
const dataStore = useDataStore()

const thing_id = route.params.id.toString()
const thingName = ref('')
const datastreams = ref([])
const showDeleteModal = ref(false)
const selectedDatastream = ref(null)

function showModal(datastream) {
  selectedDatastream.value = datastream
  showDeleteModal.value = true
}

async function onDatastreamDeleted() {
  await dataStore.fetchOrGetFromCache(
    `thing_${thing_id}`,
    `/things/${thing_id}`
  )
  const thing = dataStore[`thing_${thing_id}`]
  thingName.value = thing.name
  datastreams.value = thing.datastreams
}

let cachedThingName = `thing_${thing_id}`

dataStore
  .fetchOrGetFromCache(cachedThingName, `/things/${thing_id}`)
  .then(() => {
    const thing = dataStore[cachedThingName]
    thingName.value = thing.name
    datastreams.value = thing.datastreams
    console.log('Datastreams', datastreams)
  })
  .catch((error) => {
    console.error('Error fetching thing data from API', error)
  })
</script>

<style scoped lang="scss">
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

.action-link {
  color: #007bff;
  text-decoration: none;
  cursor: pointer;
}

.action-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

.action-link-separator {
  margin-left: 5px;
  margin-right: 5px;
}
</style>
