<template>
  <v-container>
    <v-row>
      <v-col>
        <h6 class="text-h6 mb-6">Data Source File Configuration</h6>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-radio-group
          v-model="store.formMode"
          inline
        >
          <v-radio
            label="New Data Source"
            value="create"
            :disabled="Boolean(!store.datastreamId && store.dataSourceId)"
          ></v-radio>
          <v-radio
            label="Existing Data Source"
            value="edit"
            :disabled="Boolean(!store.datastreamId && !store.dataSourceId)"
          ></v-radio>
        </v-radio-group>
      </v-col>
      <v-col v-if="store.datastreamId && store.formMode === 'edit'">
        <v-autocomplete
          ref="dataSource"
          v-model="store.dataSource"
          label="Data Source"
          :items="store.dataSources"
          item-title="name"
          :rules="[
            (val) => !!val || 'Must select a data source.'
          ]"
        ></v-autocomplete>
      </v-col>
      <v-col v-else>
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
    </v-row>
    <v-row>
      <v-col>
        <v-autocomplete
          ref="dataLoader"
          v-model="store.dataLoader"
          label="Data Loader"
          :items="store.dataLoaders"
          item-title="name"
          item-value="id"
          :rules="[
            (val) => !!val || 'Must select a data loader.'
          ]"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        ></v-autocomplete>
      </v-col>
      <v-col>
        <v-text-field
          ref="localFilePath"
          v-model="store.localFilePath"
          label="Local File Path"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter data source path.'
          ]"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
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
            (val) => val == null || val === '' || val > 0 || 'File header row must be greater than zero.',
            (val) => val == null || val === '' || val < store.dataStartRow || 'File header row must be less than the data start row.',
            (val) => val == null || val === '' || val === parseInt(val, 10) || 'File header row must be an integer.'
          ]"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
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
            (val) => val == null || val === parseInt(val, 10) || 'Data start row must be an integer.'
          ]"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useDataSourceFormStore } from '@/store/datasource_form';

const store = useDataSourceFormStore()

const dataSourceName = ref()
const dataSource = ref()
const dataLoader = ref()
const localFilePath = ref()
const remoteFileUrl = ref()
const fileHeaderRow = ref()
const dataStartRow = ref()

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
    store.fillForm()
  }
)

watch(
  () => store.formMode,
  () => {
    if (store.datastreamId && store.formMode === 'create') {
      store.dataSource = undefined
      store.fillForm()
    }
  }
)

async function validate() {
  let errors = []

  if (store.formMode === 'create' || store.dataSourceId) {
    errors.push(...(await dataSourceName.value.validate()))
  } else {
    errors.push(...(await dataSource.value.validate()))
  }

  errors.push(...(await localFilePath.value.validate()))
  errors.push(...(await dataLoader.value.validate()))
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