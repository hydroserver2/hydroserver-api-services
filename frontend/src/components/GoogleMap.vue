<template>
  <div ref="mapContainer" class="fill-width fill-height" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'
import { Thing } from '@/types'

const props = defineProps({
  markers: { type: Array<Thing>, default: [] },
  mapOptions: {
    type: Object,
    default: { center: { lat: 39, lng: -100 }, zoom: 4 },
  },
  clickable: { type: Boolean, default: false },
})
const emit = defineEmits(['location-clicked'])

const loader = new Loader({
  apiKey: import.meta.env.VITE_APP_GOOGLE_MAPS_API_KEY,
})
const map = ref<google.maps.Map>()
const mapContainer = ref<HTMLDivElement>()

async function loadMap() {
  await loader.load()
  if (mapContainer.value) {
    map.value = new google.maps.Map(mapContainer.value, props.mapOptions)
  }
}

function loadMarkers() {
  return props.markers.map((markerData: Thing) => {
    if (markerData && map.value) {
      const marker = new google.maps.Marker({
        position: new google.maps.LatLng(
          markerData.latitude,
          markerData.longitude
        ),
        map: map.value,
      })
      const content = `
            <h5>${markerData.name}</h5>
            <p><a href="/sites/${markerData.id}">View data for this site</a>
      `
      // TODO: figure out how this data will be populated
      // <p><b>
      //   ${markerData.state ? markerData.state : ''}
      //   ${markerData.country ? markerData.country : ''}
      // </b></p>
      // <p>${markerData.description}</p>

      const infoWindow = new google.maps.InfoWindow({ content })
      marker.addListener('click', () =>
        infoWindow.open({ anchor: marker, map: map.value })
      )
      return marker
    }
    return null
  })
}

function addLocationClicking() {
  const elevator = new google.maps.ElevationService()
  const geocoder = new google.maps.Geocoder()
  let newMarker: google.maps.Marker | null = null

  if (map.value) {
    map.value.addListener('click', (mapsMouseEvent: any) => {
      elevator
        .getElevationForLocations({ locations: [mapsMouseEvent.latLng] })
        .then(({ results }) => {
          if (!results[0]) return console.log('No results found')

          const locationData: any = {
            latitude: mapsMouseEvent.latLng.lat().toFixed(6),
            longitude: mapsMouseEvent.latLng.lng().toFixed(6),
            elevation: Math.round(results[0].elevation),
            state: undefined,
            country: undefined,
          }

          if (newMarker) {
            newMarker.setMap(null)
          }
          newMarker = new google.maps.Marker({
            position: mapsMouseEvent.latLng,
            map: map.value,
          })

          geocoder.geocode(
            { location: mapsMouseEvent.latLng },
            function (results, status) {
              if (status !== 'OK') {
                return console.log('Geocoder failed due to: ' + status)
              }

              if (!results?.length) {
                return console.log('No results found')
              }

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
}

onMounted(async () => {
  await loadMap()
  loadMarkers()
  if (props.clickable) addLocationClicking()
  console.log('markers', props.markers)
})
</script>
