import { Thing } from '@/types'

type MarkerData = Thing

export function useMarkers() {
  let infoWindow: google.maps.InfoWindow | null = null

  function generateMarkerContent(markerData: MarkerData): string {
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

  const createMarker = (
    markerData: MarkerData,
    map: google.maps.Map | null
  ) => {
    if (!markerData || !map) return null
    const marker = new google.maps.Marker({
      position: new google.maps.LatLng(
        markerData.latitude,
        markerData.longitude
      ),
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

  const loadMarkers = (things: MarkerData[], map: google.maps.Map | null) => {
    if (!things || !map) return []

    map.addListener('click', () => {
      if (infoWindow) infoWindow.close()
    })

    return things
      .map((thing) => createMarker(thing, map))
      .filter((marker): marker is google.maps.Marker => marker !== null)
  }

  return { loadMarkers }
}
