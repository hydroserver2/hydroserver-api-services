<template>
  <v-container>
    <v-card flat>
      <v-card-title>
        <span class="text-h5">
          {{ formTitle }}
        </span>
      </v-card-title>
      <v-card-item v-if="store.formReady">
        <DataSourceLocation
          ref="dataSourceLocationForm"
          v-if="step === 1"
        />
        <DataSourceSchedule
          ref="dataSourceScheduleForm"
          v-if="step === 2"
        />
        <DataSourceTimestamp
          ref="dataSourceTimestampForm"
          v-if="step === 3"
        />
      </v-card-item>
      <v-card-item v-else>
        Loading...
      </v-card-item>
      <v-card-actions>
        <div class="text-subtitle-2">
          * indicates a required field.
        </div>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          @click="handleCancel"
        >
          Cancel
        </v-btn>
        <v-btn
          v-if="step > 1"
          variant="text"
          @click="step--"
        >
          Previous
        </v-btn>
        <v-btn
          v-if="step < 3"
          variant="text"
          @click="handleNextPage"
        >
          Next
        </v-btn>
        <v-btn
          v-if="step === 3"
          variant="text"
          @click="handleSaveChanges"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataSourceFormStore } from '@/store/datasource_form';
import { useRoute, useRouter } from 'vue-router'
import DataSourceLocation from "@/components/DataSource/DataSourceLocation.vue";
import DataSourceSchedule from "@/components/DataSource/DataSourceSchedule.vue";
import DataSourceTimestamp from "@/components/DataSource/DataSourceTimestamp.vue";

const props = defineProps(['dataSourceId'])
const emit = defineEmits(['closeDialog'])

const step = ref(1)
const store = useDataSourceFormStore()
const route = useRoute()
const router = useRouter()

const dataSourceLocationForm = ref()
const dataSourceScheduleForm = ref()
const dataSourceTimestampForm = ref()
const dataSourceDatastreamForm = ref()
const formTitle = ref()

store.dataSourceId = props.dataSourceId || null
store.formReady = false

store.fetchDataSource().then(() => {
  store.fetchDataLoaders().then(() => {
    store.fillForm()
    store.formReady = true
  })
})

if (store.dataSourceId) {
  formTitle.value = 'Edit Data Source'
} else {
  formTitle.value = 'Add Data Source'
}

async function handleSaveChanges() {
  let valid = await dataSourceTimestampForm.value.validate()
  if (valid === true) {
    let saved = await store.saveDataSource()
    if (saved) {
      emit('closeDialog')
    } else {
      alert('Encountered an unexpected error while saving this data source.')
    }
  }
}

async function handleNextPage() {
  let form = null
  switch(step.value) {
    case 1:
      form = dataSourceLocationForm
      break;
    case 2:
      form = dataSourceScheduleForm
      break;
    case 3:
      form = dataSourceTimestampForm
      break;
  }

  if (store.dataSource != null) {
    step.value++
  } else {
    let valid = await form?.value.validate()
    if (valid === true) {
      step.value++
    }
  }
}

function handleCancel() {
  emit('closeDialog')
}

</script>

<style scoped>

</style>