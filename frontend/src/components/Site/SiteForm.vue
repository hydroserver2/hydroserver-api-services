<template>
  <v-card>
    <v-card-title class="text-h5">Register a Site</v-card-title>
    <div class="flex-shrink-0" style="height: 20rem">
      <GoogleMap
        clickable
        @location-clicked="onMapLocationClicked"
        :mapOptions="mapOptions"
        :markers="[thing]"
      />
    </div>
    <v-divider></v-divider>
    <v-card-text
      class="text-subtitle-2 text-medium-emphasis d-flex align-center"
    >
      <v-icon class="mr-1">mdi-information</v-icon>Click on the map to update
      Site Location data.
    </v-card-text>

    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4">Site Information</h6>
          <v-form
            ref="form"
            @submit.prevent="uploadThing"
            enctype="multipart/form-data"
          >
            <v-row>
              <v-col cols="12"
                ><v-text-field
                  label="Site Code"
                  v-model="thing.sampling_feature_code"
              /></v-col>
              <v-col cols="12"
                ><v-text-field label="Site Name" v-model="thing.name"
              /></v-col>
              <v-col cols="12"
                ><v-textarea
                  label="Site Description"
                  v-model="thing.description"
              /></v-col>
              <v-col cols="12"
                ><v-autocomplete
                  label="Select Site Type"
                  :items="siteTypes"
                  v-model="thing.site_type"
                ></v-autocomplete
              ></v-col>
            </v-row>
          </v-form>
        </v-col>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4">Site Location</h6>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                label="Latitude"
                v-model="thing.latitude"
                type="number"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field
                label="Longitude"
                v-model="thing.longitude"
                type="number"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field
                label="Elevation"
                v-model="thing.elevation"
                type="number"
            /></v-col>
                              <v-text-field label="State" v-model="thing.state" />
                <v-text-field
                  disabled
                  label="Elevation Datum"
                  v-model="thing.elevation_datum"
                />
                <v-text-field disabled label="County" v-model="thing.county" />
          </v-row>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn @click="closeDialog">Cancel</v-btn>
      <v-btn color="primary" @click="uploadThing">Save</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import GoogleMap from '../GoogleMap.vue'
import { useThingStore } from '@/store/things'
import { Thing } from '@/types'

const thingStore = useThingStore()
const props = defineProps({ thingId: String })
const emit = defineEmits(['close'])

const mapOptions = ref({
  center: { lat: 39, lng: -100 },
  zoom: 4,
  mapTypeId: 'roadmap',
})
const thing = reactive<Thing>({
  id: '',
  name: '',
  description: '',
  sampling_feature_type: '',
  sampling_feature_code: '',
  site_type: '',
  latitude: null as number,
  longitude: null as number,
  elevation: null as number,
  state: '',
  county: '',
  is_primary_owner: false,
  owns_thing: false,
  follows_thing: false,
  owners: [],
  followers: 0,
})

const siteTypes = [
  'Atmosphere',
  'Borehole',
  'Ditch',
  'Estuary',
  'House',
  'Lake, Reservoir, Impoundment',
  'Land',
  'Laboratory or sample-preparation area',
  'Observation well',
  'Other',
  'Pavement',
  'Soil hole',
  'Spring',
  'Stream',
  'Stream gage',
  'Storm sewer',
  'Tidal stream',
  'Water quality station',
  'Weather station',
  'Wetland',
]

async function populateThing(id: string) {
  await thingStore.fetchThings()
  Object.assign(thing, thingStore.things[id])
  mapOptions.value = {
    center: { lat: thing.latitude, lng: thing.longitude },
    zoom: 8,
    mapTypeId: 'satellite',
  }
}

function closeDialog() {
  emit('close')
}

function uploadThing() {
  if (thing) {
    if (props.thingId) thingStore.updateThing(thing)
    else thingStore.createThing(thing)
  }
  emit('close')
}

function onMapLocationClicked(locationData: Thing) {
  thing.latitude = parseFloat(locationData.latitude)
  thing.longitude = parseFloat(locationData.longitude)
  thing.elevation = parseFloat(locationData.elevation)
  thing.state = locationData.state
  // thing.county = locationData.county
}

onMounted(async () => {
  if (props.thingId) await populateThing(props.thingId)
})
</script>

<style scoped lang="scss"></style>
