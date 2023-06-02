<template>
  <div class="d-flex fill-height">
    <v-navigation-drawer v-model="drawer" app width="350" class="sidebar">
      <v-row>
        <v-spacer></v-spacer>
        <v-col cols="auto">
          <v-btn v-if="drawer" class="toggler" icon @click="drawer = !drawer">
            <v-icon>mdi-menu-open</v-icon>
          </v-btn>
        </v-col>
      </v-row>

      <v-card-title>Browse Data Collection Sites</v-card-title>
      <v-card-text>
        <div class="d-flex my-2">
          <v-spacer></v-spacer>
          <v-btn-secondary @click="clearFilters">Clear Filters</v-btn-secondary>
        </div>
        <SearchBar
          :items="organizations"
          :clear-search="clearSearch"
          @filtered-items="handleFilteredOrganizations"
        />
        <div v-for="organization in filteredOrganizations">
          <p>{{ organization }}</p>
        </div>
        <v-expansion-panels class="mt-4">
          <v-expansion-panel title="Site Types">
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
      </v-card-text>
    </v-navigation-drawer>

    <v-btn v-if="!drawer" class="toggler" icon @click="drawer = !drawer">
      <v-icon>mdi-menu</v-icon>
    </v-btn>

    <GoogleMap
      :key="filteredThings"
      :things="filteredThings"
      :mapOptions="{ center: { lat: 39, lng: -100 }, zoom: 4 }"
    />
  </div>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SearchBar from '@/components/SearchBar.vue'
import { computed, onMounted, ref } from 'vue'
import { Ref } from 'vue'
import { Thing } from '@/types'
import { useThingStore } from '@/store/things'

const drawer = ref(true)
const thingStore = useThingStore()
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
const selectedSiteTypes: Ref<any[]> = ref([])
const filteredOrganizations: Ref<string[]> = ref([])
const filteredOrganizationsSet = ref(new Set())

const organizations = computed(() => {
  const allOrgs = new Set()

  Object.values(thingStore.things).forEach((thing) => {
    thing.owners.forEach((owner) => {
      if (owner.organization) {
        allOrgs.add(owner.organization)
      }
    })
  })

  return Array.from(allOrgs)
})

const filteredThings: any = computed(() => {
  if (typeof thingStore.things !== 'object' || !thingStore.things) return []
  return Object.values(thingStore.things).filter(isThingValid)
})

function handleFilteredOrganizations(filtered: any) {
  filteredOrganizations.value = [...filtered]
  filteredOrganizationsSet.value = new Set([...filtered])
}

function isThingValid(thing: Thing) {
  const orgValid =
    filteredOrganizationsSet.value.size === 0 ||
    thing.owners.some((owner) =>
      filteredOrganizationsSet.value.has(owner.organization)
    )
  const siteTypeValid =
    selectedSiteTypes.value.length === 0 ||
    selectedSiteTypes.value.includes(thing.site_type)

  return orgValid && siteTypeValid
}

function clearFilters() {
  selectedSiteTypes.value = []
  filteredOrganizations.value = []
  filteredOrganizationsSet.value = new Set()
  clearSearch.value = !clearSearch.value
}

onMounted(() => {
  thingStore.fetchThings()
})
</script>

<style scoped lang="scss">
.v-card.sidebar {
  flex-basis: 35rem;
  height: 100%;
  overflow: auto;
}
</style>
