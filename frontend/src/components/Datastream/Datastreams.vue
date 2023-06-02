<template>
  <v-container>
    <h2 class="text-h4 mb-4">Manage Site Datastreams</h2>
    <h5 class="text-h5 mb-4">{{ thingStore.things[thing_id]?.name }}</h5>

    <v-row class="pb-2">
      <v-col>
        <v-btn
          variant="elevated"
          density="comfortable"
          color="green"
          :to="{ name: 'DatastreamForm', params: { id: thing_id } }"
          >Add New Datastream</v-btn
        >
      </v-col>
    </v-row>
    <v-data-table
      class="elevation-3"
      :headers="headers"
      :items="datastreamStore.datastreams[thing_id]"
    >
      <template v-slot:item.actions="{ item }">
        <router-link
          :to="{
            name: 'DatastreamForm',
            params: { id: thing_id, datastreamId: item.raw.id },
          }"
        >
          <v-icon color="grey" small> mdi-pencil </v-icon>
        </router-link>

        <v-icon color="grey" small @click="showModal(item.raw)">
          mdi-delete
        </v-icon>

        <v-icon
          small
          color="grey"
          @click="toggleVisibility(item.raw)"
          v-if="item.raw.is_visible"
        >
          mdi-eye
        </v-icon>
        <v-icon
          small
          color="grey-lighten-1"
          @click="toggleVisibility(item.raw)"
          v-else
        >
          mdi-eye-off
        </v-icon>
      </template>
    </v-data-table>
    <v-dialog v-if="selectedDatastream" v-model="showDeleteModal" width="40rem">
      <v-card>
        <v-card-title>
          <span class="text-h5">Confirm Deletion</span>
        </v-card-title>
        <v-card-text>
          Are you sure you want to permanently delete the this datastream and
          all the observations associated with it?
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
    <v-row class="pt-2">
      <v-col>
        <v-btn
          color="secondary"
          :to="{ name: 'SingleSite', params: { id: thing_id } }"
        >
          <v-icon left>mdi-arrow-left</v-icon>
          Back to Site Details
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDatastreamStore } from '@/store/datastreams'
import { useThingStore } from '@/store/things'
import { Datastream } from '@/types'
import { Ref } from 'vue'

const headers = ref([
  { title: 'ObservedProperty', key: 'observed_property_name' },
  { title: 'Method / Sensor', key: 'method_name' },
  { title: 'Units', key: 'unit_name' },
  { title: 'Processing Level', key: 'processing_level_name' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
])

const route = useRoute()
const datastreamStore = useDatastreamStore()
const thingStore = useThingStore()

const thing_id = route.params.id.toString()

const showDeleteModal = ref(false)
const selectedDatastream: Ref<Datastream | null> = ref(null)

function showModal(datastream: Datastream) {
  selectedDatastream.value = datastream
  showDeleteModal.value = true
}

async function toggleVisibility(datastream: Datastream) {
  datastream.is_visible = !datastream.is_visible
  await datastreamStore.setVisibility(datastream.id, datastream.is_visible)
}

async function deleteDatastream() {
  showDeleteModal.value = false
  if (selectedDatastream.value) {
    await datastreamStore.deleteDatastream(
      selectedDatastream.value.id,
      thing_id
    )
  }
}

onMounted(async () => {
  await datastreamStore.fetchDatastreamsByThingId(thing_id)
  await thingStore.fetchThingById(thing_id)
})
</script>
