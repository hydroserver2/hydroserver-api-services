<template>
  <div class="manage-datastreams" style="margin: 1rem">
    <h1>Manage Site Datastreams</h1>
    <h2>{{ thingStore.things[thing_id]?.name }}</h2>
    <v-btn
      style="margin-top: 0.5rem; margin-bottom: 1rem"
      color="primary"
      :to="{ name: 'DatastreamForm', params: { id: thing_id } }"
      >Add New Datastream</v-btn
    >

    <ManagerTable
      :names="datastreamNameMappings"
      :rows="datastreamStore.datastreams[thing_id]"
    >
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
import { useApiClient } from '@/utils/api-client'
const api = useApiClient()
import ManagerTable from '@/components/ManagerTable.vue'
import { useDatastreamStore } from '@/store/datastreams'
import { useThingStore } from '@/store/things'

type NameTuple = [string, string]

const datastreamNameMappings = ref<NameTuple[]>([
  ['observed_property_name', 'ObservedProperty'],
  ['method_name', 'Method / Sensor'],
  ['unit_name', 'Units'],
  ['processing_level_name', 'ProcessingLevel'],
])

const route = useRoute()
const datastreamStore = useDatastreamStore()
const thingStore = useThingStore()

const thing_id = route.params.id.toString()

const showDeleteModal = ref(false)
const selectedDatastream = ref(null)

function showModal(datastream) {
  selectedDatastream.value = datastream
  showDeleteModal.value = true
}

async function toggleVisibility(datastream) {
  await datastreamStore.setVisibility(datastream.id, !datastream.is_visible)
  datastream.is_visible = !datastream.is_visible
}

async function deleteDatastream() {
  showDeleteModal.value = false
  await datastreamStore.deleteDatastream(selectedDatastream.value.id, thing_id)
}

onMounted(async () => {
  await datastreamStore.fetchDatastreamsByThingId(thing_id)
  await thingStore.fetchThingById(thing_id)
})
</script>
