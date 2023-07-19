<template>
  <div class="d-flex fill-height">
    <v-navigation-drawer v-model="drawer" app width="350">
      <v-row>
        <v-spacer></v-spacer>
        <v-col cols="auto">
          <v-btn
            color="cancel"
            v-if="drawer"
            class="toggler"
            icon
            @click="drawer = !drawer"
          >
            <v-icon>mdi-menu-open</v-icon>
          </v-btn>
        </v-col>
      </v-row>

      <v-card-title>Browse Data Collection Sites</v-card-title>
      <v-card-text>
        <div class="d-flex my-2">
          <v-btn-cancel @click="clearFilters">Clear Filters</v-btn-cancel>
          <v-spacer></v-spacer>
          <v-btn-primary @click="filterOrganizations">Search</v-btn-primary>
        </div>
        <form @submit.prevent="filterOrganizations">
          <v-text-field
            placeholder="Filter by Organizations"
            prepend-inner-icon="mdi-magnify"
            v-model="searchInput"
            clearable
          />
        </form>
        <p v-if="!validFilter" class="text-error">No results found</p>
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
import { computed, onMounted, ref } from 'vue'
import { Ref } from 'vue'
import { Thing } from '@/types'
import { useThingStore } from '@/store/things'
import { siteTypes } from '@/vocabularies'

const drawer = ref(true)
const thingStore = useThingStore()
const selectedSiteTypes: Ref<string[]> = ref([])
const filteredOrganizations = ref(new Set())
const searchInput = ref('')
const validFilter = ref(true)

const organizations = computed(() => {
  const allOrgs = new Set()
  Object.values(thingStore.things).forEach((thing) => {
    thing.owners.forEach((owner) => {
      if (owner.organization) {
        allOrgs.add(owner.organization.toLowerCase())
      }
    })
  })
  return Array.from(allOrgs)
})

const filterOrganizations = () => {
  if (!searchInput || !searchInput.value) {
    filteredOrganizations.value = new Set([...organizations.value])
  } else {
    const lowerCase = searchInput.value.toLowerCase()
    filteredOrganizations.value = new Set([
      ...organizations.value.filter((org: any) => org.includes(lowerCase)),
    ])
  }
  validFilter.value = filteredOrganizations.value.size === 0 ? false : true
}

const filteredThings: any = computed(() => {
  if (typeof thingStore.things !== 'object' || !thingStore.things) return []
  return Object.values(thingStore.things).filter(isThingValid)
})

function isThingValid(thing: Thing) {
  const orgValid =
    filteredOrganizations.value.size === 0 ||
    thing.owners.some((owner) =>
      filteredOrganizations.value.has(owner.organization.toLowerCase())
    )
  const siteTypeValid =
    selectedSiteTypes.value.length === 0 ||
    selectedSiteTypes.value.includes(thing.site_type)

  return orgValid && siteTypeValid
}

function clearFilters() {
  selectedSiteTypes.value = []
  filteredOrganizations.value = new Set()
  validFilter.value = true
  searchInput.value = ''
}

onMounted(async () => {
  await thingStore.fetchThings()
})
</script>
