export const clearMarkers = (markers: google.maps.Marker[]) => {
  if (!markers) return
  markers.forEach((marker) => marker.setMap(null))
  markers.splice(0, markers.length)
}

export async function getElevation(position: google.maps.LatLngLiteral) {
  const elevator = new google.maps.ElevationService()
  const { results } = await elevator.getElevationForLocations({
    locations: [position],
  })
  if (!results[0]) throw new Error('No elevation found')
  return results[0]
}

export async function getGeoData(position: google.maps.LatLngLiteral) {
  try {
    const geocoder = new google.maps.Geocoder()
    const { results } = await geocoder.geocode({
      location: position,
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

export function addMarker(
  map: google.maps.Map,
  markers: google.maps.Marker[],
  position: google.maps.LatLngLiteral
) {
  const marker = new google.maps.Marker({ position, map })
  markers.push(marker)
}

export async function fetchLocationData(position: google.maps.LatLngLiteral) {
  const { elevation }: any = await getElevation(position)
  const { state, county }: any = await getGeoData(position)

  return {
    latitude: position.lat.toFixed(6),
    longitude: position.lng.toFixed(6),
    elevation: Math.round(elevation),
    state: state,
    county: county,
  }
}

export function useSingleMarkerMode(
  map: google.maps.Map,
  markers: google.maps.Marker[],
  onLocationFetched: (locationData: any) => void
) {
  map.addListener('click', async (mapsMouseEvent: any) => {
    const position = {
      lat: mapsMouseEvent.latLng.lat(),
      lng: mapsMouseEvent.latLng.lng(),
    }
    clearMarkers(markers)
    addMarker(map, markers, position)
    const locationData = await fetchLocationData(position)
    onLocationFetched(locationData)
  })
}
