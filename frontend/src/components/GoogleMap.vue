<template>
  <div ref="mapContainer" class="fill-width fill-height" />
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Loader } from '@googlemaps/js-api-loader'
import { Thing } from '@/types'

const props = defineProps({
  things: { type: Array<Thing>, default: [] },
  mapOptions: {
    type: Object,
    default: { center: { lat: 39, lng: -100 }, zoom: 4 },
  },
  clickable: Boolean,
})
const emit = defineEmits(['location-clicked'])

const loader = new Loader({
  apiKey: import.meta.env.VITE_APP_GOOGLE_MAPS_API_KEY,
})
let map: google.maps.Map | null = null
let markers: google.maps.Marker[]
const mapContainer = ref<HTMLElement>()
let infoWindow: google.maps.InfoWindow | null = null

const clearMarkers = () => {
  if (!markers) return
  markers.forEach((marker) => marker.setMap(null))
  markers = []
}

function generateMarkerContent(markerData: Thing): string {
  return `
      <h6 class="text-h6 pb-1">${markerData.name}</h6>
      <p class="pb-1"><b>
        ${markerData.county ? markerData.county : ''}
        ${markerData.county && markerData.state ? ',' : ''}
        ${markerData.state ? markerData.state : ''}
      </b></p>
      <p class="pb-1">${markerData.description}</p>
      <p class="pt-1">
        <a href="/sites/${markerData.id}">View data for this site</a>
      </p>`
}

function createMarker(
  markerData: Thing,
  map: google.maps.Map | null
): google.maps.Marker | null {
  if (!markerData || !map) return null
  const marker = new google.maps.Marker({
    position: new google.maps.LatLng(markerData.latitude, markerData.longitude),
    map: map,
  })

  const content = generateMarkerContent(markerData)

  marker.addListener('click', (e: any) => {
    if (infoWindow) infoWindow.close()
    infoWindow = new google.maps.InfoWindow({ content })
    infoWindow.open({ anchor: marker, map: map })
    e.stop()
  })
  return marker
}

function loadMarkers() {
  clearMarkers()
  if (!props.things) return
  markers = props.things
    .map((thing) => createMarker(thing, map))
    .filter((marker): marker is google.maps.Marker => marker !== null)
}

async function addLocationClicking() {
  if (!map) return
  const elevator = new google.maps.ElevationService()
  const geocoder = new google.maps.Geocoder()

  map.addListener('click', async (mapsMouseEvent: any) => {
    const { elevation }: any = await getElevation(mapsMouseEvent, elevator)
    const { state, county }: any = await getGeoData(mapsMouseEvent, geocoder)

    const locationData: any = {
      latitude: mapsMouseEvent.latLng.lat().toFixed(6),
      longitude: mapsMouseEvent.latLng.lng().toFixed(6),
      elevation: Math.round(elevation),
      state: state,
      county: county,
    }
    emit('location-clicked', locationData)

    clearMarkers()
    markers.push(
      new google.maps.Marker({
        position: mapsMouseEvent.latLng,
        map: map,
      })
    )
  })
}

async function getElevation(mapsMouseEvent: any, elevator: any) {
  const { results } = await elevator.getElevationForLocations({
    locations: [mapsMouseEvent.latLng],
  })
  if (!results[0]) throw new Error('No elevation found')
  return results[0]
}

async function getGeoData(mapsMouseEvent: any, geocoder: any) {
  try {
    const { results } = await geocoder.geocode({
      location: mapsMouseEvent.latLng,
    })

    const { state, county } = results[0].address_components.reduce(
      (acc: any, component: any) => {
        if (component.types.includes('administrative_area_level_1'))
          acc.state = component.short_name
        if (component.types.includes('administrative_area_level_2'))
          acc.county = component.short_name
        return acc
      },
      { state: '', county: '' }
    )

    return { state, county }
  } catch (error) {
    console.error(`Failed to get geolocation data: ${error}`)
  }
}

onMounted(async () => {
  let attempts = 0
  const intervalId = setInterval(async () => {
    attempts++
    if (mapContainer && mapContainer.value) {
      clearInterval(intervalId)

      const google = await loader.load()

      const mapOptions = {
        ...props.mapOptions,
        styles: [
          {
            featureType: 'poi',
            stylers: [{ visibility: 'off' }],
          },
          {
            featureType: 'transit',
            stylers: [{ visibility: 'off' }],
          },
          {
            featureType: 'landscape',
            elementType: 'labels',
            stylers: [{ visibility: 'off' }],
          },
        ],
      }
      map = new google.maps.Map(mapContainer.value, mapOptions)
      if (props.clickable) await addLocationClicking()
      loadMarkers()

      if (map) {
        map.addListener('click', () => {
          if (infoWindow) infoWindow.close()
        })
      }
    } else if (attempts >= 30) {
      // 30 attempts * 100ms = 3 seconds
      clearInterval(intervalId)
      console.error('mapContainer is still not initialized after 3 seconds!')
    }
  }, 100) // 100ms interval
})
</script>

<style>
a {
  text-decoration: none;
  color: #1565c0;
  text-transform: uppercase;
}

a:hover {
  color: #0d47a1;
}
</style>
