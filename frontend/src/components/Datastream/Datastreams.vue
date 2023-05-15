<template>
  <div class="manage-datastreams" style="margin: 1rem">
    <h1>Manage Site Datastreams</h1>
    <h2>{{ thing?.name }}</h2>
    <v-btn
      style="margin-top: 0.5rem; margin-bottom: 1rem"
      color="primary"
      :to="{ name: 'DatastreamForm', params: { id: thing_id } }"
      >Add New Datastream</v-btn
    >

    <ManagerTable :names="datastreamNameMappings" :rows="datastreams">
      <template v-slot:actions="{ row }">
        <router-link
          class="action-link"
          :to="{
            name: 'DatastreamForm',
            params: { id: thing_id, datastreamId: row.id },
          }"
          >Edit
        </router-link>
        <span> | </span>
        <a @click="showModal(row)">Delete</a>
        <span> | </span>
        <a
          v-if="row.is_visible"
          class="action-link"
          @click="toggleVisibility(row)"
          >Hide
        </a>
        <a v-else @click="toggleVisibility(row)">Make visible</a>
      </template>
    </ManagerTable>

    <v-dialog v-if="selectedDatastream" v-model="showDeleteModal" width="40rem">
      <v-card>
        <v-card-title>
          <span class="text-h5">Confirm Deletion</span>
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the following datastream? This is
          unrecoverable and will delete all associated observations
          <br />
          <br />
          <strong>ID:</strong> {{ selectedDatastream.id }} <br />
        </v-card-text>
        <v-card-actions>
          <v-btn color="red" @click="showDeleteModal = false">Cancel</v-btn>
          <v-btn color="green" @click="deleteDatastream">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-btn
      color="secondary"
      :to="{ name: 'SingleSite', params: { id: thing_id } }"
      >Back to Site Details</v-btn
    >
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/store/data'
import ManagerTable from '@/components/ManagerTable.vue'
import { useApiClient } from '@/utils/api-client'
const api = useApiClient()

type NameTuple = [string, string]

const datastreamNameMappings = ref<NameTuple[]>([
  ['observed_property_name', 'ObservedProperty'],
  ['method_name', 'Method / Sensor'],
  ['unit_name', 'Units'],
  ['processing_level_name', 'ProcessingLevel'],
])

const route = useRoute()
const dataStore = useDataStore()

const thing_id = route.params.id.toString()
const cachedThingName = `thing_${thing_id}`
const thing = ref(null)
const datastreams = ref([])
const showDeleteModal = ref(false)
const selectedDatastream = ref(null)

function showModal(datastream) {
  console.log(datastream)
  selectedDatastream.value = datastream
  showDeleteModal.value = true
}

async function toggleVisibility(datastream) {
  try {
    await api.put(`/datastreams/${datastream.id}`, {
      is_visible: !datastream.is_visible,
    })
    datastream.is_visible = !datastream.is_visible
    thing.value.datastreams = datastreams
    dataStore.cacheProperty(cachedThingName, thing.value)
  } catch (error) {
    console.error(error)
  }
}

async function deleteDatastream() {
  showDeleteModal.value = false
  await api.delete(`/datastreams/${selectedDatastream.value.id}`)
  localStorage.removeItem(cachedThingName)
  await dataStore.fetchOrGetFromCache(cachedThingName, `/things/${thing_id}`)
  thing.value = dataStore[cachedThingName]
  datastreams.value = thing.value.datastreams
}

onMounted(async () => {
  try {
    await dataStore.fetchOrGetFromCache(cachedThingName, `/things/${thing_id}`)
    thing.value = dataStore[cachedThingName]
    datastreams.value = thing.value.datastreams
  } catch (error) {
    console.error('Error fetching thing data from API', error)
  }
})
</script>
