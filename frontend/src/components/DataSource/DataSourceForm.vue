<template>
  <v-container>
    <v-card flat>
      <v-card-title>
        <span class="text-h5">Link Data Source</span>
      </v-card-title>
      <v-card-item>
        <DataSourcePreview v-if="false"/>
      </v-card-item>
      <v-card-item>
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
        <DataSourceDatastream
          ref="dataSourceDatastreamForm"
          v-if="step === 4"
        />
      </v-card-item>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          v-if="step > 1"
          variant="text"
          @click="step--"
        >
          Previous
        </v-btn>
        <v-btn
          v-if="step < 4"
          variant="text"
          @click="handleNextPage"
        >
          Next
        </v-btn>
        <v-btn
          v-if="step === 4"
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
import DataSourceDatastream from "@/components/DataSource/DataSourceDatastream.vue";
import DataSourcePreview from "@/components/DataSource/DataSourcePreview.vue";


const step = ref(1)
const store = useDataSourceFormStore()
const route = useRoute()
const router = useRouter()

const dataSourceLocationForm = ref()
const dataSourceScheduleForm = ref()
const dataSourceTimestampForm = ref()
const dataSourceDatastreamForm = ref()

store.fetchDataSources()
store.fetchDataLoaders()
store.datastreamId = route.params.datastreamId?.toString() || null

async function handleSaveChanges() {
  let valid = await dataSourceDatastreamForm.value.validate()
  if (valid === true) {
    let saved = await store.saveDataSource()
    if (saved) {
      router.back()
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

</script>

<style scoped>

</style>