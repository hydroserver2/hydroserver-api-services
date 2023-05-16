<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="4">
        <h1>Browse Data Collection Sites</h1>
        <v-btn color="teal-lighten-1" @click="clearFilters">Clear Filters</v-btn
        ><br /><br />
        <h3>Filter by Organizations</h3>
        <SearchBar
          :items="organizations"
          :clear-search="clearSearch"
          @filtered-items="handleFilteredOrganizations"
        />
        <div v-for="organization in filteredOrganizations">
          <p>{{ organization }}</p>
        </div>
        <v-expansion-panels class="custom-expansion-panel">
          <v-expansion-panel title="Site Types" color="teal-lighten-1">
            <v-expansion-panel-text>
              <template v-for="type in siteTypes" :key="type">
                <v-checkbox
                  v-model="selectedSiteTypes"
                  :label="type"
                  :value="type"
                />
              </template>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
      <v-col cols="12" md="8">
        <GoogleMap
          :markers="filteredMarkers"
          :mapOptions="{ center: { lat: 39, lng: -100 }, zoom: 4 }"
          style="width: 100%; height: 80vh"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SearchBar from '@/components/SearchBar.vue'
import { computed, onMounted, ref } from 'vue'
import { useMarkerStore } from '@/store/markers'

const markerStore = useMarkerStore()
const siteTypes = ref([
  'Borehole',
  'Ditch',
  'Atmosphere',
  'Estuary',
  'House',
  'Land',
  'Pavement',
  'Stream',
  'Spring',
  'Lake, Reservoir, Impoundment',
  'Laboratory or sample-preparation area',
  'Observation well',
  'Soil hole',
  'Storm sewer',
  'Stream gage',
  'Tidal stream',
  'Water quality station',
  'Weather station',
  'Wetland',
  'Other',
])
const clearSearch = ref(false)
const selectedSiteTypes = ref([])
const filteredOrganizations = ref([])
const filteredOrganizationsSet = ref(new Set())

const organizations = computed(() => {
  if (!Array.isArray(markerStore.markers)) return []
  const allOrgs = new Set()
  markerStore.markers.forEach((marker) => {
    marker.owners.forEach((owner) => {
      if (owner.organization) {
        allOrgs.add(owner.organization)
      }
    })
  })
  return Array.from(allOrgs)
})

const filteredMarkers = computed(() => {
  if (!Array.isArray(markerStore.markers)) return []
  return markerStore.markers.filter(isMarkerValid)
})

function handleFilteredOrganizations(filtered) {
  filteredOrganizations.value = filtered
  filteredOrganizationsSet.value = new Set(filtered)
}

function isMarkerValid(marker) {
  const orgValid =
    filteredOrganizationsSet.value.size === 0 ||
    marker.owners.some((owner) =>
      filteredOrganizationsSet.value.has(owner.organization)
    )
  const siteTypeValid =
    selectedSiteTypes.value.length === 0 ||
    selectedSiteTypes.value.includes(marker.site_type)

  return orgValid && siteTypeValid
}

function clearFilters() {
  selectedSiteTypes.value = []
  filteredOrganizations.value = []
  filteredOrganizationsSet.value = new Set()
  clearSearch.value = !clearSearch.value
}

onMounted(async () => {
  await markerStore.fetchMarkers()
  console.log('markers', markerStore.markers)
})
</script>
