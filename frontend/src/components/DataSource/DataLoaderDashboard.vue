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
        </v-toolbar>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn
          disabled
          icon="mdi-delete"
        />
      </template>
    </v-data-table>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataLoaderDashboardStore } from '@/store/dataloader_dashboard'


const store = useDataLoaderDashboardStore()
const search = ref()
const dataLoaderRowSelected = ref()

store.fetchDataLoaders()

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