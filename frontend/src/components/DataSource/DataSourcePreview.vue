<template>
  <v-container class="flex-table-container pt-0">
    <v-data-table
      class="flex-table hide-footer file-previewer"
      :headers="tableHeaders"
      :items="tableItems"
      fixed-header
      density="compact"
      style="border: 1px"
    >

    </v-data-table>
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