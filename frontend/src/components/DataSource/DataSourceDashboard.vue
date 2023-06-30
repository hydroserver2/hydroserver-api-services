<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="auto">
        <h5 class="text-h5">My Data Sources Dashboard</h5>
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
<!--          <v-switch-->
<!--            v-model="locationVisible"-->
<!--            label="Show File Location?"-->
<!--          />-->
          <v-spacer></v-spacer>
          <v-btn
            disabled
            icon="mdi-plus"
          />
          <v-btn
            disabled
            icon="mdi-dots-vertical"
          />
        </v-toolbar>
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
              disabled
              v-bind="props"
              icon="mdi-dots-vertical"
            />
          </template>
          <v-list>
            <v-list-item
              title="Edit Data Source"
              prepend-icon="mdi-pencil"
            />
            <v-list-item
              title="Delete Data Source"
              prepend-icon="mdi-delete"
            />
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataSourceDashboardStore } from '@/store/datasource_dashboard'

const store = useDataSourceDashboardStore()

const search = ref()
const locationVisible = ref(false)

store.fetchDataSources()

const headers = [
  {
    title: 'Name',
    align: 'start',
    sortable: true,
    key: 'name',
  },
  {
    title: 'Status',
    align: 'start',
    sortable: true,
    key: 'status',
  },
  {
    title: 'Linked Datastreams',
    align: 'start',
    sortable: true,
    key: 'linked_datastreams'
  },
  {
    title: 'Data Source Thru',
    align: 'start',
    sortable: true,
    key: 'data_source_thru',
  },
  {
    title: 'HydroServer Thru',
    align: 'start',
    sortable: true,
    key: 'database_thru',
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