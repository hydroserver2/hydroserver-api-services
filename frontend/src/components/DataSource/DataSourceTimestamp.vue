<template>
  <v-container>
    <v-row>
      <v-col>
        <h6 class="text-h6 mb-6">Data Source Timestamp</h6>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-radio-group
          v-model="store.timestampType"
          inline
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        >
          <v-radio
            label="Column Index"
            value="index"
          ></v-radio>
          <v-radio
            label="Column Name"
            value="name"
          ></v-radio>
        </v-radio-group>
      </v-col>
      <v-col v-if="store.timestampType === 'index'" class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="timestampColumnIndex"
          v-model.number="store.timestampColumn"
          label="Timestamp Column"
          hint="Enter the column index that contains timestamps for the datastreams."
          persistent-hint
          type="number"
          :rules="[
             (val) => val != null || 'Column index is required.',
             (val) => +val === parseInt(val, 10) || 'Interval must be an integer.',
             (val) => +val > 0 || 'Column index must be greater than zero.'
          ]"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        />
      </v-col>
      <v-col v-if="store.timestampType === 'name'" class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="timestampColumnName"
          v-model="store.timestampColumn"
          label="Timestamp Column"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter timestamp column name.'
          ]"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-radio-group
          v-model="store.timestampFormat"
          inline
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        >
          <v-radio
            label="ISO 8601 Format"
            value="iso"
          ></v-radio>
          <v-radio
            label="Custom Format"
            value="custom"
          ></v-radio>
        </v-radio-group>
      </v-col>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="timestampCustomFormat"
          v-model="store.timestampCustomFormat"
          label="Timestamp Format"
          :disabled="Boolean(store.timestampFormat !== 'custom' || (store.datastreamId && store.dataSource != null))"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter timestamp format.'
          ]"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-switch
          v-model="store.timestampUseTimezoneOffset"
          label="Append Timezone Offset?"
          :disabled="Boolean(store.datastreamId && store.dataSource != null)"
        ></v-switch>
      </v-col>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-autocomplete
          v-model="store.timestampTimezoneOffset"
          label="Timezone Offset"
          :disabled="Boolean(store.timestampUseTimezoneOffset === false || (store.datastreamId && store.dataSource != null))"
          :items="timezoneOffsets"
        ></v-autocomplete>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useDataSourceFormStore } from '@/store/datasource_form';

const store = useDataSourceFormStore()

const timestampColumnIndex = ref()
const timestampColumnName = ref()
const timestampCustomFormat = ref()

const timezoneOffsets = ref([
  '-1200', '-1100', '-1000', '-0900', '-0800', '-0700', '-0600', '-0500', '-0430', '-0400', '-0330', '-0300', '-0200',
  '-0100', '+0000', '+0100', '+0200', '+0300', '+0330', '+0400', '+0430', '+0500', '+0530', '+0545', '+0600', '+0630',
  '+0700', '+0800', '+0845', '+0900', '+0930', '+1000', '+1030', '+1100', '+1130', '+1200', '+1245', '+1300', '+1400'
])

async function validate() {
  let errors = []

  if (store.timestampFormat === 'custom') {
    errors.push(...(await timestampCustomFormat.value.validate()))
  }

  if (store.timestampType === 'index') {
    errors.push(...(await timestampColumnIndex.value.validate()))
  } else if (store.timestampType === 'name') {
    errors.push(...(await timestampColumnName.value.validate()))
  }

  return errors.length === 0
}

defineExpose({
  validate
})

</script>

<style scoped>

</style>