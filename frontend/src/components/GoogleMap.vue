<template>
  <div ref="mapDiv" style="width: 100%; height: 30vh" />
</template>

<script setup lang="ts">
import { ref, onMounted, Ref } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'

const props = defineProps({
  markers: { type: Array, default: [] },
  mapOptions: {
    type: Object,
    default: { center: { lat: 39, lng: -100 }, zoom: 4 },
  },
  clickable: { type: Boolean, default: false },
})
const emit = defineEmits(['location-clicked'])

const loader = new Loader({
  apiKey: import.meta.env.VUE_APP_GOOGLE_MAPS_API_KEY,
})
let map: Ref<google.maps.Map | null> = ref(null)
const mapDiv: Ref<HTMLDivElement | null> = ref(null)

async function loadMap() {
  await loader.load()
  map = new google.maps.Map(mapDiv.value, props.mapOptions)
}

function loadMarkers() {
  return props.markers.map((markerData) => {
    if (markerData) {
      const latLng = new google.maps.LatLng(
        markerData.latitude,
        markerData.longitude
      )
      let marker = new google.maps.Marker({ position: latLng, map })
      const content = `
            <h5>${markerData.name}</h5>
            <p><b>${markerData.city ? markerData.city : ''}
                   ${markerData.state ? markerData.state : ''}
                   ${markerData.country ? markerData.country : ''}
            </b></p>
            <p>${markerData.description}</p>
            <p><a href="/sites/${markerData.id}">View data for this site</a>`
      const infoWindow = new google.maps.InfoWindow({ content })
      marker.addListener('click', () =>
        infoWindow.open({ anchor: marker, map })
      )
      return marker
    }
    return null
  })
}

function addLocationClicking() {
  const elevator = new google.maps.ElevationService()
  const geocoder = new google.maps.Geocoder()
  let new_marker = null

  map.addListener('click', (mapsMouseEvent) => {
    elevator
      .getElevationForLocations({ locations: [mapsMouseEvent.latLng] })
      .then(({ results }) => {
        if (!results[0]) return console.log('No results found')

        const locationData = {
          latitude: mapsMouseEvent.latLng.lat().toFixed(6),
          longitude: mapsMouseEvent.latLng.lng().toFixed(6),
          elevation: Math.round(results[0].elevation),
          state: undefined,
          country: undefined,
        }

        if (new_marker) new_marker.setMap(null)
        new_marker = new google.maps.Marker({
          position: mapsMouseEvent.latLng,
          map: map,
        })

        geocoder.geocode(
          { location: mapsMouseEvent.latLng },
          function (results, status) {
            if (status !== 'OK')
              return console.log('Geocoder failed due to: ' + status)
            if (!results[0]) return console.log('No results found')

            const { state, country } = results[0].address_components.reduce(
              (acc, component) => {
                if (component.types.includes('administrative_area_level_1'))
                  acc.state = component.short_name
                if (component.types.includes('country'))
                  acc.country = component.short_name
                return acc
              },
              { state: '', country: '' }
            )
            locationData.state = state
            locationData.country = country
            emit('location-clicked', locationData)
          }
        )
      })
      .catch((e) => console.log('Elevation service failed due to: ' + e))
  })
}

onMounted(async () => {
  await loadMap()
  loadMarkers()
  if (props.clickable) addLocationClicking()
})
</script>
