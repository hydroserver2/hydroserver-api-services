<template>
  <v-container>
    <v-row>
      <v-col>
        <h6 class="text-h6 mb-6">Data Source File Configuration</h6>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-text-field
          ref="dataSourceName"
          v-model="store.dataSourceName"
          label="Data Source Name *"
          hint="Enter a name you can use to identify this data source."
          persistent-hint
          :rules="[
            (val: string) => val !== '' && val != null || 'Must enter data source name.',
            (val: string) => /^[0-9a-zA-Z ... ]+$/.test(val) || 'Invalid data source name.',
          ]"
        ></v-text-field>
      </v-col>
      <v-col>
        <v-autocomplete
          ref="dataLoader"
          v-model="store.dataLoader"
          label="Data Loader *"
          hint="Select the data loader which will load this data source."
          persistent-hint
          :items="store.dataLoaders"
          item-title="name"
          item-value="id"
          :rules="[
            (val: string) => !!val || 'Must select a data loader.'
          ]"
        ></v-autocomplete>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-text-field
          ref="localFilePath"
          v-model="store.localFilePath"
          label="Local File Path *"
          hint="Enter the absolute path to the data source file."
          persistent-hint
          :rules="[
            (val: string) => val !== '' && val != null || 'Must enter data source path.'
          ]"
        />
      </v-col>
      <v-col>
        <v-select
          v-model="store.fileDelimiter"
          label="File Delimiter *"
          hint="Select the type of delimiter used for this data file."
          persistent-hint
          :items="intervalUnitValues"
          variant="outlined"
          density="comfortable"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-text-field
          ref="fileHeaderRow"
          v-model.number="store.fileHeaderRow"
          label="File Header Row"
          hint="Enter the row that contains file headers, if any."
          persistent-hint
          type="number"
          clearable
          :rules="[
            (val: number) => val == null || val > 0 || 'File header row must be greater than zero.',
            (val: number) => val == null || val < store.dataStartRow || 'File header row must be less than the data start row.',
            (val: number) => val == null || val === Math.floor(val) || 'File header row must be an integer.'
          ]"
        />
      </v-col>
      <v-col>
        <v-text-field
          ref="dataStartRow"
          v-model.number="store.dataStartRow"
          label="Data Start Row *"
          hint="Enter the row that data starts on."
          persistent-hint
          type="number"
          :rules="[
            (val: number) => val > 0 || 'Data start row must be greater than zero.',
            (val: number) => store.fileHeaderRow == null || val > store.fileHeaderRow || 'Data start row must be greater than the file header row.',
            (val: number) => val == null || val === parseInt(val, 10) || 'Data start row must be an integer.'
          ]"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useDataSourceFormStore } from '@/store/datasource_form'

const store = useDataSourceFormStore()

const dataSourceName = ref()
const dataSource = ref()
const dataLoader = ref()
const localFilePath = ref()
const fileHeaderRow = ref()
const dataStartRow = ref()

const intervalUnitValues = [
  { value: ',', title: 'Comma' },
  { value: '|', title: 'Pipe' },
  { value: '\\t', title: 'Tab' },
  { value: ';', title: 'Semicolon' },
  { value: ' ', title: 'Space' },
]

watch(
  () => store.fileHeaderRow,
  () => {
    if (
      store.fileHeaderRow !== undefined &&
      store.fileHeaderRow >= store.dataStartRow
    ) {
      store.dataStartRow = store.fileHeaderRow + 1
    }
  }
)

async function validate() {
  let errors = []

  errors.push(...(await dataSourceName.value.validate()))
  errors.push(...(await localFilePath.value.validate()))
  errors.push(...(await dataLoader.value.validate()))
  errors.push(...(await fileHeaderRow.value.validate()))
  errors.push(...(await dataStartRow.value.validate()))

  return errors.length === 0
}

defineExpose({
  validate,
})
</script>

<style scoped></style>
