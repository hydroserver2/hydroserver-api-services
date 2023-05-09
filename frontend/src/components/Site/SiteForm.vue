<template>
  <v-card>
    <v-card-title class="text-h5">Register a Site</v-card-title>
    <div class="flex-shrink-0" style="height: 20rem">
      <GoogleMap
        v-if="markerLoaded"
        @location-clicked="onMapLocationClicked"
        clickable
        :mapOptions="mapOptions"
        :markers="[marker]"
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
            @submit.prevent="createThing"
            enctype="multipart/form-data"
          >
            <v-row>
              <v-col cols="12"
                ><v-text-field
                  label="Site Code"
                  v-model="formData.sampling_feature_code"
              /></v-col>
              <v-col cols="12"
                ><v-text-field label="Site Name" v-model="formData.name"
              /></v-col>
              <v-col cols="12"
                ><v-textarea
                  label="Site Description"
                  v-model="formData.description"
              /></v-col>
              <v-col cols="12"
                ><v-autocomplete
                  label="Select Site Type"
                  :items="siteTypes"
                  v-model="formData.site_type"
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
                v-model="formData.latitude"
                type="number"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field
                label="Longitude"
                v-model="formData.longitude"
                type="number"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field
                label="Elevation"
                v-model="formData.elevation"
                type="number"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field
                label="Elevation Datum"
                v-model="formData.elevation_datum"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field label="State" v-model="formData.state"
            /></v-col>
            <v-col cols="12" sm="6"
              ><v-text-field label="Country" v-model="formData.country"
            /></v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn @click="closeDialog">Cancel</v-btn>
      <v-btn color="primary" @click="createThing">Save</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDataStore } from '@/store/data'
import GoogleMap from '../GoogleMap.vue'
import { useApiClient } from '@/utils/api-client'
const api = useApiClient()
const props = defineProps({ thingId: String })
const emit = defineEmits(['close', 'siteCreated'])

const formData = ref({
  name: '',
  description: '',
  sampling_feature_type: '',
  sampling_feature_code: '',
  site_type: null,
  latitude: null,
  longitude: null,
  elevation: null,
  state: '',
  country: '',
})

const mapOptions = ref({ center: { lat: 39, lng: -100 }, zoom: 4 })
let marker = ref(null)
let markerLoaded = ref(false)
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

// TODO: move method implementation to api wrapper
async function populateThing() {
  const dataStore = useDataStore()
  try {
    await dataStore.fetchOrGetFromCache(
      `thing_${props.thingId}`,
      `/things/${props.thingId}`
    )
    marker.value = dataStore[`thing_${props.thingId}`]
    markerLoaded.value = true
    for (const key in formData.value) {
      if (marker.value.hasOwnProperty(key)) {
        formData.value[key] = marker.value[key]
      }
    }
    mapOptions.value = {
      center: { lat: marker.value.latitude, lng: marker.value.longitude },
      zoom: 8,
      mapTypeId: 'satellite',
    }
  } catch (error) {
    console.log('Error Fetching Thing: ', error)
  }
}

if (props.thingId) {
  populateThing()
} else {
  markerLoaded.value = true
}

function closeDialog() {
  emit('close')
}

// TODO: move method implementation to api wrapper
async function createThing() {
  const axiosMethod = props.thingId ? api.patch : api.post
  const endpoint = props.thingId ? `/things/${props.thingId}` : '/things'

  try {
    const response = await axiosMethod(endpoint, formData.value)

    const updatedThing = response.data
    const dataStore = useDataStore()
    if (!props.thingId) dataStore.addThing(updatedThing)
    else {
      localStorage.removeItem(`thing_${props.thingId}`)
      localStorage.removeItem('things')
    }
    emit('close')
    emit('siteCreated')
  } catch (error) {
    console.log('Error Registering Site: ', error)
  }
}

function onMapLocationClicked(locationData) {
  formData.value.latitude = locationData.latitude
  formData.value.longitude = locationData.longitude
  formData.value.elevation = locationData.elevation
  formData.value.state = locationData.state
  formData.value.country = locationData.country
}
</script>

<style scoped lang="scss"></style>
