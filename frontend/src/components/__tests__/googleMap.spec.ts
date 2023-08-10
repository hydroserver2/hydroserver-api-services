import { describe, it, expect } from 'vitest'
import { loadMap } from '@/composables/loadMap'
import {
  clearMarkers,
  addMarker,
  getElevation,
  getGeoData,
  fetchLocationData,
  useSingleMarkerMode,
} from '@/composables/mapUtils'

describe('Google Maps', () => {
  it('Dummy test to make sure vitest is working', () => {
    let markers: google.maps.Marker[] = []
    clearMarkers(markers)
    expect(markers).toEqual([])
  })
})
