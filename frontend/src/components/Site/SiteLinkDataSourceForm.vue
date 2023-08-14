<template>
  <v-container>
    <v-card flat>
      <v-card-title>
        <span class="text-h5">
          {{ formTitle }}
        </span>
      </v-card-title>
      <v-card-item v-if="store.formLoaded === true">
        <v-row class="pa-2">
          <v-col class="v-col-xs-12 v-col-sm-6">
            <v-autocomplete
              v-model="store.selectedDataSource"
              label="Data Source"
              placeholder="No Linked Data Source"
              persistent-placeholder
              hint="Select the data source for this datastream."
              persistent-hint
              clearable
              :items="store.dataSources"
              item-title="name"
              @update:modelValue="handleUpdateDataSource"
            />
          </v-col>
          <v-col v-if="!store.selectedDataSource">
            <v-text-field
              label="Datastream Column"
              hint="Enter the column name/index containing values for this datastream."
              persistent-hint
              disabled
            />
          </v-col>
          <v-col v-else>
            <v-text-field
              ref="datastreamColumnName"
              v-model="store.selectedColumn"
              label="Datastream Column *"
              hint="Enter the column name/index containing values for this datastream."
              :type="
                (store.selectedDataSource.file_access || {}).header_row === 0
                  ? 'number'
                  : 'text'
              "
              :rules="[
                (val: string) => !!val || 'Must enter the column containing the datastream.'
              ]"
              persistent-hint
            />
          </v-col>
        </v-row>
      </v-card-item>
      <v-card-item v-else>
        <v-row>
          <v-col> LOADING... </v-col>
        </v-row>
      </v-card-item>
      <v-card-actions>
        <div class="text-subtitle-2">* indicates a required field.</div>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="handleCancel"> Cancel </v-btn>
        <v-btn variant="text" :disabled="!store.savable" @click="handleSave">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSiteLinkDataSourceFormStore } from '@/store/datasource_link'

const props = defineProps(['thingId', 'datastreamId', 'dataSourceId', 'column'])
const emit = defineEmits(['closeDialog'])

const store = useSiteLinkDataSourceFormStore()
const datastreamColumnName = ref()

store.formLoaded = false

store.fetchDatastreams(props.thingId, props.datastreamId).then((datastream) => {
  store.fillForm(
    props.datastreamId,
    datastream.data_source_id,
    datastream.column
  )
  store.fetchDataSources().then(() => {
    store.formLoaded = true
  })
})

let formTitle = props.dataSourceId
  ? 'Edit Linked Data Source'
  : 'Link Data Source'

function handleUpdateDataSource() {
  if (store.selectedDataSource === (store.linkedDataSource || {}).name) {
    store.selectedColumn = store.linkedColumn
  } else {
    store.selectedColumn = undefined
  }
}

async function handleSave() {
  let valid = []
  if (datastreamColumnName.value) {
    valid = await datastreamColumnName.value.validate()
  }
  if (valid.length === 0) {
    let response = await store.saveDataSource()
    if (response.status === 200) {
      emit('closeDialog')
    } else {
      alert('Encountered an unexpected error updating linked data source.')
    }
  }
}

function handleCancel() {
  emit('closeDialog')
}
</script>

<style scoped></style>
