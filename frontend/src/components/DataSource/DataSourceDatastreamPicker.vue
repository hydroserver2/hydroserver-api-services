<template>
  <v-data-table
    :headers="datastreamColumns"
    :items="[...store.datastreamRows.map((row: any) => { return {...row} })]"
  >
    <template v-slot:item.column="{ item }">
      <v-menu
        v-model="item.menu"
        :close-on-content-click="false"
        @keydown.enter="handleUpdateColumn(item.raw.id)"
      >
        <template v-slot:activator="{ props }">
          <v-chip
            v-if="item.raw.column"
            v-bind="props"
            @click="columnInput=item.raw.column"
          >
            {{ item.raw.column }}
          </v-chip>
          <v-btn
            v-else
            v-bind="props"
            icon="mdi-plus-circle"
            color="secondary"
            @click="columnInput=null"
          />
        </template>
        <v-card width="300">
          <v-text-field
            v-model="columnInput"
            append-inner-icon="mdi-check-circle"
            label="Column"
            hint="Enter the file column name/index for this datastream."
            persistent-hint
            variant="plain"
            class="pa-3"
            clearable
            @click:appendInner="handleUpdateColumn(item.raw.id)"
          />
        </v-card>
      </v-menu>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataSourceFormStore } from '@/store/datasource_form';

const store = useDataSourceFormStore()

const columnInput = ref()

if (store.datastreams.length === 0) {
  store.fetchDatastreams()
} else {
  store.datastreams = [...store.datastreams]
}

function handleUpdateColumn(datastreamId: string) {
  if (columnInput.value == null || columnInput.value === '') {
    store.datastreamColumns = store.datastreamColumns.filter(column => column.id !== datastreamId)
  } else if (store.datastreamColumns.map(column => column.id).includes(datastreamId)) {
    store.datastreamColumns = store.datastreamColumns.map((column) => {
      if (datastreamId === column.id) {
        return {
          id: column.id,
          column: columnInput.value
        }
      } else {
        return column
      }
    })
  } else {
    store.datastreamColumns.push({
      id: datastreamId,
      column: columnInput.value
    })
  }
}

const datastreamColumns = [
  {
    title: 'Column',
    align: 'start',
    sortable: true,
    key: 'column',
  },
  {
    title: 'Datastream ID',
    align: 'start',
    sortable: true,
    key: 'id',
    width: 340
  },
  {
    title: 'Thing ID',
    align: 'start',
    sortable: true,
    key: 'thing_id',
    width: 340
  },
  {
    title: 'Method',
    align: 'start',
    sortable: true,
    key: 'method_name',
  },
  {
    title: 'Observation Type',
    align: 'start',
    sortable: true,
    key: 'observation_type',
  },
  {
    title: 'Observed Property',
    align: 'start',
    sortable: true,
    key: 'observed_property_name',
  },
  {
    title: 'Processing Level Name',
    align: 'start',
    sortable: true,
    key: 'processing_level_name',
  },
  {
    title: 'Result Type',
    align: 'start',
    sortable: true,
    key: 'result_type',
  },
  {
    title: 'Sampled Medium',
    align: 'start',
    sortable: true,
    key: 'sampled_medium',
  },
  {
    title: 'Status',
    align: 'start',
    sortable: true,
    key: 'status',
  },
  {
    title: 'Unit',
    align: 'start',
    sortable: true,
    key: 'unit_name',
  },
]

</script>

<style scoped>

</style>