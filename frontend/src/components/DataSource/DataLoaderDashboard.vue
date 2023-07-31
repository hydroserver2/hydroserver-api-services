<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="auto">
        <h5 class="text-h5">My Data Loaders Dashboard</h5>
      </v-col>
    </v-row>
    <v-data-table
      :headers="headers"
      :items="store.dataLoaderRows"
      :search="search"
      hover
      class="elevation-3"
    >
      <template v-slot:top>
        <v-toolbar
          flat
        >
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
          <v-spacer></v-spacer>
          <v-btn
            prepend-icon="mdi-download-circle"
            color="primary"
            variant="elevated"
            :to="{
              name: 'HydroLoader'
            }"
          >
            Download HydroLoader
          </v-btn>
        </v-toolbar>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn
          disabled
          icon="mdi-delete"
          @click="handleOpenConfirmDelete(item.raw.id)"
        />
      </template>
    </v-data-table>
        <v-dialog
      v-model="confirmDeleteOpen"
      max-width="500"
    >
      <v-card>
        <v-card-title>
          Confirm Delete Data Loader
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the following data loader?
        </v-card-text>
        <v-card-text>
          • {{ store.dataLoaderRows.filter(row => row.id === dataLoaderRowSelected)[0].name }}
        </v-card-text>
        <v-card-text>
          Note: You should uninstall this data loader instance before deleting it here. Deleting this data loader
                instance will unlink it from all associated data sources.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            @click="confirmDeleteOpen = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="red"
            :disabled="deletingDataLoader"
            @click="handleDeleteDataLoader"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataLoaderDashboardStore } from '@/store/dataloader_dashboard'


const store = useDataLoaderDashboardStore()
const search = ref()
const confirmDeleteOpen = ref(false)
const deletingDataLoader = ref(false)
const dataLoaderRowSelected = ref()

store.fetchDataLoaders()

function handleOpenConfirmDelete(dataLoaderId: string) {
  dataLoaderRowSelected.value = dataLoaderId
  confirmDeleteOpen.value = true
}

function handleDeleteDataLoader() {
  deletingDataLoader.value = true
  store.deleteDataLoader(dataLoaderRowSelected.value).then(() => {
    confirmDeleteOpen.value = false
    deletingDataLoader.value = false
    store.fetchDataLoaders()
  })
}

const headers = [
  {
    title: 'Name',
    align: 'start',
    sortable: true,
    key: 'name',
  },
  {
    title: 'Last Communication',
    align: 'start',
    sortable: true,
    key: 'last_communication'
  },
  {
    title: 'Actions',
    align: 'end',
    sortable: false,
    key: 'actions',
  },
]


</script>

<style scoped>

</style>