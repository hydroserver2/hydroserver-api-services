<template>
  <v-container>
    <v-row>
      <v-col>
        <v-radio-group
          v-model="store.mode"
          inline
        >
          <v-radio
            label="New Data Source"
            value="create"
          ></v-radio>
          <v-radio
            label="Existing Data Source"
            value="edit"
          ></v-radio>
        </v-radio-group>
      </v-col>
      <v-col v-if="store.mode === 'create'">
        <v-text-field
          ref="dataSourceName"
          v-model="store.dataSourceName"
          label="Data Source Name"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter data source name.',
            (val) => /^[0-9a-zA-Z ... ]+$/.test(val) || 'Invalid data source name.',
          ]"
        ></v-text-field>
      </v-col>
      <v-col v-if="store.mode === 'edit'">
        <v-autocomplete
          v-model="store.dataSource"
          label="Data Source"
          :items="store.dataSources"
          item-title="name"
        ></v-autocomplete>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-radio-group
          v-model="store.dataSourceType"
          inline
          :disabled="store.dataSource != null"
        >
          <v-radio
            label="Local File"
            value="local"
          ></v-radio>
          <v-radio
            label="Remote File"
            value="remote"
          ></v-radio>
        </v-radio-group>
      </v-col>
      <v-col v-if="store.dataSourceType === 'local'">
        <v-text-field
          ref="localFilePath"
          v-model="store.localFilePath"
          label="Local File Path"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter data source path.'
            // (val) => /^\/.*$/.test(val) || 'Invalid data source path.'
          ]"
          :disabled="store.dataSource != null"
        />
      </v-col>
      <v-col v-if="store.dataSourceType === 'remote'">
        <v-text-field
          ref="remoteFileUrl"
          v-model="store.remoteFileUrl"
          label="Remote File URL"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter data source URL.'
          ]"
          :disabled="store.dataSource != null"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-text-field
          ref="fileHeaderRow"
          v-model.number="store.fileHeaderRow"
          label="File Header Row"
          type="number"
          clearable
          :rules="[
            (val) => val == null || val > 0 || 'File header row must be greater than zero.',
            (val) => val == null || val < store.dataStartRow || 'File header row must be less than the data start row.',
          ]"
          :disabled="store.dataSource != null"
        />
      </v-col>
      <v-col>
        <v-text-field
          ref="dataStartRow"
          v-model.number="store.dataStartRow"
          label="Data Start Row"
          type="number"
          :rules="[
            (val) => val > 0 || 'Data start row must be greater than zero.',
            (val) => store.fileHeaderRow == null || val > store.fileHeaderRow || 'Data start row must be greater than the file header row.',
          ]"
          :disabled="store.dataSource != null"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useDataSourceFormStore } from '@/store/datasource_form';

const store = useDataSourceFormStore()

const dataSourceName = ref()
const localFilePath = ref()
const remoteFileUrl = ref()
const fileHeaderRow = ref()
const dataStartRow = ref()

// let i = await store.fetchDataSources()

watch(
  () => store.fileHeaderRow,
  () => {
    if (store.fileHeaderRow !== undefined && store.fileHeaderRow >= store.dataStartRow) {
      store.dataStartRow = store.fileHeaderRow + 1
    }
  }
)

watch(
  () => store.dataSource,
  () => {
    store.loadDataSource()
  }
)

watch(
  () => store.mode,
  () => {
    if (store.mode === 'create') {
      store.dataSource = undefined
    }
  }
)

async function validate() {
  let errors = []

  if (store.mode === 'create') {
    errors.push(...(await dataSourceName.value.validate()))
  }

  if (store.dataSourceType === 'local') {
    errors.push(...(await localFilePath.value.validate()))
  } else if (store.dataSourceType === 'remote') {
    errors.push(...(await remoteFileUrl.value.validate()))
  }

  errors.push(...(await fileHeaderRow.value.validate()))
  errors.push(...(await dataStartRow.value.validate()))

  return errors.length === 0
}

defineExpose({
  validate
})

</script>

<style scoped>

</style>