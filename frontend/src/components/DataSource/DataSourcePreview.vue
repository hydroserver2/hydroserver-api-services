<template>
  <v-container class="flex-table-container pt-0">
    <v-row>
      <v-col>
        <h6 class="text-h6 mb-6">Data Source Preview</h6>
      </v-col>
    </v-row>


    <v-data-table
      v-if="false"
      class="flex-table hide-footer file-previewer"
      :headers="tableHeaders"
      :items="tableItems"
      fixed-header
      density="compact"
      style="border: 1px"
    >

    </v-data-table>
    <v-card
      v-else
      title="Preview Placeholder"
      flat
      style="height: 100px"
    />
  </v-container>
</template>

<script setup lang="ts">

let tableHeaders = [
  { title: '',  key: '&index', sortable: false, fixed: true, width: 30},
  { title: 'A', key: 'A', sortable: false },
  { title: 'B', key: 'B', sortable: false },
  { title: 'C', key: 'C', sortable: false },
  { title: 'D', key: 'D', sortable: false },
]
let tableItems = [
  { '&index': 1, A: 13, B: 14, C: 16, D: 19 },
  { '&index': 2, A: 13, B: 14, C: 16, D: 19 },
  { '&index': 3, A: 13, B: 14, C: 16, D: 19 },
  { '&index': 4, A: 13, B: 14, C: 16, D: 19 },
]

</script>

<style scoped>

</style>