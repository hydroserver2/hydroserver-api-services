<template>
  <v-card>
    <v-card-title class="text-h5">
      Register a Site
      <v-spacer></v-spacer>
    </v-card-title>
    <v-card-text>
      <v-container fluid>
        <v-row>
          <v-col cols="12" md="6">
            <v-form
              ref="form"
              @submit.prevent="uploadThing"
              enctype="multipart/form-data"
            >
              <v-text-field
                label="Site Code"
                v-model="thing.sampling_feature_code"
              />
              <v-text-field label="Site Name" v-model="thing.name" />
              <v-textarea
                label="Site Description"
                v-model="thing.description"
              />
              <v-autocomplete
                label="Select Site Type"
                :items="siteTypes"
                v-model="thing.site_type"
              ></v-autocomplete>
            </v-form>
          </v-col>
          <v-col cols="12" md="6" v-if="thing">
            <GoogleMap
              clickable
              @location-clicked="onMapLocationClicked"
              :mapOptions="mapOptions"
              :markers="[thing]"
            />
            Click on the map to update site coordinates and elevation data.
            <br /><br /><br />
            <h2>Site Location</h2>
            <br />
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  label="Latitude"
                  v-model="thing.latitude"
                  type="number"
                />
                <v-text-field
                  label="Elevation"
                  v-model="thing.elevation"
                  type="number"
                />
                <!--                <v-text-field label="State" v-model="thing.state" />-->
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  label="Longitude"
                  v-model="thing.longitude"
                  type="number"
                />
                <!--                <v-text-field-->
                <!--                  label="Elevation Datum"-->
                <!--                  v-model="thing.elevation_datum"-->
                <!--                />-->
                <!--                <v-text-field label="Country" v-model="thing.country" />-->
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="error" @click="emit('close')">Cancel</v-btn>
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
const emit = defineEmits(['close', 'siteCreated'])

const mapOptions = ref({
  center: { lat: 39, lng: -100 },
  zoom: 4,
  mapTypeId: 'roadmap',
})
let thing = reactive<Thing>({
  id: '',
  name: '',
  description: '',
  sampling_feature_type: '',
  sampling_feature_code: '',
  site_type: '',
  latitude: 0,
  longitude: 0,
  elevation: 0,
  state: '',
  county: '',
  is_primary_owner: false,
  owns_thing: false,
  follows_thing: false,
  owners: [],
  followers: 0,
})

const siteTypes = ref([
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
])

async function populateThing() {
  if (!props.thingId) return
  await thingStore.fetchThingById(props.thingId)
  thing = thingStore[props.thingId]
  mapOptions.value = {
    center: { lat: thing.latitude, lng: thing.longitude },
    zoom: 8,
    mapTypeId: 'satellite',
  }
}

onMounted(async () => {
  if (props.thingId) await populateThing()
})

function uploadThing() {
  if (thing) {
    if (props.thingId) thingStore.updateThing(thing)
    else thingStore.createThing(thing)
  }
  emit('close')
  emit('siteCreated')
}

function onMapLocationClicked(locationData) {
  thing.latitude = locationData.latitude
  thing.longitude = locationData.longitude
  thing.elevation = locationData.elevation
  // thing.state = locationData.state
  // thing.country = locationData.country
}
</script>
