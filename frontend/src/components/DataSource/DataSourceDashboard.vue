<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="auto">
        <h5 class="text-h5">Manage Data Sources</h5>
      </v-col>
    </v-row>
    <v-data-table
      :headers="headers"
      :items="store.dataSourceRows"
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
            color="secondary"
            prepend-icon="mdi-plus"
            variant="elevated"
            @click="handleAddDataSource"
          >
            Add Data Source
          </v-btn>
        </v-toolbar>
      </template>
      <template v-slot:item.status="{ item }">
        <v-chip v-if="item.columns.status === 'ok'" color="green">
          Up-To-Date
        </v-chip>
        <v-chip v-if="item.columns.status === 'pending'" color="blue">
          Pending
        </v-chip>
        <v-chip v-if="item.columns.status === 'bad'" color="red">
          Needs Attention
        </v-chip>
        <v-chip v-if="item.columns.status === 'stale'" color="orange">
          Behind Schedule
        </v-chip>
        <v-chip v-if="item.columns.status === 'unknown'" color="gray">
          Unknown
        </v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn
          disabled
          v-if="item.raw.paused === true"
          icon="mdi-play"
        />
        <v-btn
          disabled
          v-else
          icon="mdi-pause"
        />
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              icon="mdi-dots-vertical"
            />
          </template>
          <v-list>
            <v-list-item
              title="Data Source Details"
              prepend-icon="mdi-information"
              :to="{
                name: 'DataSource',
                params: { id: item.raw.id },
              }"
            />
            <v-list-item
              title="Edit Data Source"
              prepend-icon="mdi-pencil"
              @click="handleEditDataSource(item.raw.id)"
            />
            <v-list-item
              title="Delete Data Source"
              prepend-icon="mdi-delete"
              @click="handleOpenConfirmDelete(item.raw.id)"
            />
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
    <v-dialog
      v-model="dataSourceFormOpen"
      persistent
    >
      <DataSourceForm
        @close-dialog="handleFinishEditing"
        :dataSourceId="dataSourceRowSelected"
      />
    </v-dialog>
    <v-dialog
      v-model="confirmDeleteOpen"
      max-width="500"
    >
      <v-card>
        <v-card-title>
          Confirm Delete Data Source
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the following data source?
        </v-card-text>
        <v-card-text>
          • {{ store.dataSourceRows.filter(row => row.id === dataSourceRowSelected)[0].name }}
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
            :disabled="deletingDataSource"
            @click="handleDeleteDataSource"
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
import { useDataSourceDashboardStore } from '@/store/datasource_dashboard'
import DataSourceForm from "@/components/DataSource/DataSourceForm.vue";


const store = useDataSourceDashboardStore()
const search = ref()
const dataSourceFormOpen = ref(false)
const confirmDeleteOpen = ref(false)
const deletingDataSource = ref(false)
const dataSourceRowSelected = ref()

store.fetchDataSources()

function handleAddDataSource() {
  dataSourceRowSelected.value = null
  dataSourceFormOpen.value = true
}

function handleEditDataSource(dataSourceId: string) {
  dataSourceRowSelected.value = dataSourceId
  dataSourceFormOpen.value = true
}

function handleOpenConfirmDelete(dataSourceId: string) {
  dataSourceRowSelected.value = dataSourceId
  confirmDeleteOpen.value = true
}

function handleDeleteDataSource() {
  deletingDataSource.value = true
  store.deleteDataSource(dataSourceRowSelected.value).then(() => {
    confirmDeleteOpen.value = false
    deletingDataSource.value = false
    store.fetchDataSources()
  })
}

function handleFinishEditing() {
  dataSourceFormOpen.value = false
  store.fetchDataSources()
}

const headers = [
  {
    title: 'Name',
    align: 'start',
    sortable: true,
    key: 'name',
  },
  {
    title: 'Data Loader',
    align: 'start',
    sortable: true,
    key: 'data_loader'
  },
  {
    title: 'Status',
    align: 'start',
    sortable: true,
    key: 'status',
  },
  {
    title: 'Last Synced',
    align: 'start',
    sortable: true,
    key: 'last_synced',
  },
  {
    title: 'Next Sync',
    align: 'start',
    sortable: true,
    key: 'next_sync',
  },
  {
    title: 'Actions',
    align: 'start',
    sortable: true,
    key: 'actions',
  },
]


</script>

<style scoped>

</style>