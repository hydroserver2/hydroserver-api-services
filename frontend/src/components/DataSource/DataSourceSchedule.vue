<template>
  <v-container>
    <v-row>
      <v-col>
        <h6 class="text-h6 mb-6">Data Source Schedule</h6>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="scheduleStartTime"
          v-model="store.scheduleStartTime"
          label="Start Time"
          hint="Enter an optional start time for loading data. Otherwise, data loading will begin immediately."
          persistent-hint
          type="datetime-local"
          clearable
        />
      </v-col>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="scheduleEndTime"
          v-model="store.scheduleEndTime"
          label="End Time"
          hint="Enter an optional end time for loading data. Otherwise, data will be loaded indefinitely."
          persistent-hint
          type="datetime-local"
          clearable
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-radio-group v-model="store.scheduleType" inline>
          <v-radio label="Interval" value="interval"></v-radio>
          <v-radio label="Crontab" value="crontab"></v-radio>
        </v-radio-group>
      </v-col>
      <v-col
        v-if="store.scheduleType === 'interval'"
        class="v-col-xs-6 v-col-sm-3"
      >
        <v-text-field
          ref="interval"
          v-model="store.interval"
          label="Interval"
          hint="Enter the interval data should be loaded on."
          persistent-hint
          type="number"
          :rules="[
             (val: string) => val != null && val !== '' || 'Interval value is required.',
             (val: string) => +val === parseInt(val, 10) || 'Interval must be an integer.',
             (val: string) => +val > 0 || 'Interval must be greater than zero.'
          ]"
        />
      </v-col>
      <v-col
        v-if="store.scheduleType === 'interval'"
        class="v-col-xs-6 v-col-sm-3"
      >
        <v-select
          v-model="store.intervalUnits"
          label="Interval Units"
          :items="intervalUnitValues"
          variant="outlined"
          density="comfortable"
        />
      </v-col>
      <v-col
        v-if="store.scheduleType === 'crontab'"
        class="v-col-xs-12 v-col-sm-6"
      >
        <v-text-field
          ref="crontab"
          v-model="store.crontab"
          label="Crontab"
          hint="Enter a crontab schedule for the data to be loaded on."
          persistent-hint
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataSourceFormStore } from '@/store/datasource_form'

const store = useDataSourceFormStore()

const scheduleStartTime = ref()
const scheduleEndTime = ref()
const interval = ref()
const crontab = ref()

const intervalUnitValues = [
  { value: 'minutes', title: 'Minutes' },
  { value: 'hours', title: 'Hours' },
  { value: 'days', title: 'Days' },
]

async function validate() {
  let errors = []

  errors.push(...(await scheduleStartTime.value.validate()))
  errors.push(...(await scheduleEndTime.value.validate()))

  if (store.scheduleType === 'interval') {
    errors.push(...(await interval.value.validate()))
  } else if (store.scheduleType === 'crontab') {
    errors.push(...(await crontab.value.validate()))
  }

  return errors.length === 0
}

defineExpose({
  validate,
})
</script>

<style scoped></style>
