<template>
  <v-container>
    <div v-if="!loading">
      <v-row>
        <v-col>
          <h4 class="text-h4 mb-4">{{ store.name }}</h4>
        </v-col>
        <v-spacer/>
        <v-col class="text-right">
          <v-tooltip text="Edit Data Source" location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                color="secondary"
                icon="mdi-pencil"
                @click="dataSourceFormOpen = true"
              />
            </template>
          </v-tooltip>
          <v-tooltip text="Delete Data Source" location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                color="delete"
                icon="mdi-delete"
              />
            </template>
          </v-tooltip>
          <v-tooltip text="Refresh" location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                color="primary"
                icon="mdi-refresh"
                @click="loadDataSource"
              />
            </template>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-spacer/>
      <v-row>
        <v-col cols="12" md="6">
          <v-row>
            <v-col>
              <h5 class="text-h5">Data Source Configuration</h5>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-table class="elevation-2">
                <tbody>
                  <tr v-for="property in dataSourceProperties" :key="property.label">
                    <td><i :class="property.icon"></i></td>
                    <td>{{ property.label }}</td>
                    <td>
                      {{
                        store[property.value as keyof Object]
                      }}
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" md="6">
          <v-row>
            <v-col>
              <h5 class="text-h5">Data Source Status</h5>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-table
                :key="testkey"
                class="elevation-2"
              >
                <tbody>
                  <tr v-for="property in dataSourceSyncProperties" :key="property.label">
                    <td><i :class="property.icon"></i></td>
                    <td>{{ property.label }}</td>
                    <td>
                      {{
                        store[property.value as keyof Object]
                      }}
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <h5 class="text-h5">Linked Datastreams</h5>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            class="elevation-2"
            :headers="linkedDatastreamColumns"
            :items="store.datastreams"
          >
          </v-data-table>
        </v-col>
      </v-row>
    </div>
    <div v-else>
      Loading
    </div>
    <v-dialog
      v-model="dataSourceFormOpen"
      persistent
    >
      <DataSourceForm
        v-if="dataSourceFormOpen === true"
        @close-dialog="handleFinishEditDataSource()"
        :dataSourceId="store.id"
      />
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataSourceDetailStore } from '@/store/datasource_detail'
import { useRoute } from 'vue-router'
import DataSourceForm from "@/components/DataSource/DataSourceForm.vue";

const store = useDataSourceDetailStore()
const route = useRoute()
const loading = ref(true)
const dataSourceFormOpen = ref(false)
const testkey = ref(0)

store.id = route.params.id.toString()

function loadDataSource() {
  loading.value = true
  store.fetchDataSource().then(() => {
    testkey.value++
    loading.value = false
    testkey.value++
  })
}

function handleFinishEditDataSource() {
  dataSourceFormOpen.value = false
  loadDataSource()
}

loadDataSource()

let dataSourceProperties = [
    { icon: 'fas fa-id-badge', label: 'ID', value: 'id' },
    { icon: 'fas fa-id-badge', label: 'Name', value: 'name' },
    { icon: 'fas fa-id-badge', label: 'Data Loader', value: 'dataLoader' },
    { icon: 'fas fa-id-badge', label: 'Local File Path', value: 'filePath' },
    { icon: 'fas fa-id-badge', label: 'Header Row', value: 'headerRow' },
    { icon: 'fas fa-id-badge', label: 'Data Start Row', value: 'dataStartRow' },
    { icon: 'fas fa-id-badge', label: 'Timestamp Column', value: 'timestampColumn' },
    { icon: 'fas fa-id-badge', label: 'Timestamp Format', value: 'timestampFormat' },
    { icon: 'fas fa-id-badge', label: 'Timezone Offset', value: 'timezoneOffset' },
]

let dataSourceSyncProperties = [
    { icon: 'fas fa-id-badge', label: 'Status', value: 'status' },
    { icon: 'fas fa-id-badge', label: 'Paused', value: 'paused' },
    { icon: 'fas fa-id-badge', label: 'Schedule', value: 'scheduleValue' },
    { icon: 'fas fa-id-badge', label: 'Schedule Start Time', value: 'scheduleStartTime' },
    { icon: 'fas fa-id-badge', label: 'Schedule End Time', value: 'scheduleEndTime' },
    { icon: 'fas fa-id-badge', label: 'Last Synced', value: 'lastSynced' },
    { icon: 'fas fa-id-badge', label: 'Last Sync Message', value: 'lastSyncMessage' },
    { icon: 'fas fa-id-badge', label: 'Next Sync', value: 'nextSync' },
    { icon: 'fas fa-id-badge', label: 'Data Source Thru', value: 'dataSourceThru' },
]

let linkedDatastreamColumns = [
  {
    title: 'Name',
    align: 'start',
    sortable: true,
    key: 'name',
  },
  {
    title: 'Status',
    align: 'start',
    sortable: true,
    key: 'status',
  },
  {
    title: 'HydroServer Data Thru',
    align: 'start',
    sortable: true,
    key: 'dataThru',
  },
  {
    title: 'Data Source Column',
    align: 'start',
    sortable: true,
    key: 'column',
  }
]
</script>

<style scoped>

</style>