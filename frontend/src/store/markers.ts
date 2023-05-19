import { defineStore } from 'pinia'
import { Marker, Thing } from '@/types'
import { useApiClient } from '@/utils/api-client'

export const useMarkerStore = defineStore('markers', {
  state: () => ({ markers: [] as Marker[], loaded: false }),
  getters: {
    ownedMarkers(): Marker[] {
      return this.markers.filter((marker) => marker.owns_thing)
    },
    followedMarkers(): Marker[] {
      return this.markers.filter((thing) => thing.follows_thing)
    },
    ownedOrFollowedMarkers(): Marker[] {
      return this.markers.filter(
        (thing) => thing.owns_thing || thing.follows_thing
      )
    },
  },
  actions: {
    async addMarker(thingData: Thing) {
      try {
        let newMarker = {
          id: thingData.id,
          name: thingData.name,
          owners: thingData.owners,
          site_type: thingData.site_type,
          latitude: thingData.latitude,
          longitude: thingData.longitude,
          owns_thing: thingData.owns_thing,
          follows_thing: thingData.follows_thing,
          sampling_feature_code: thingData.sampling_feature_code,
        }
        this.markers.push(newMarker)
      } catch (error) {
        console.error('Error adding marker to marker store', error)
      }
    },
    async fetchMarkers() {
      const api = useApiClient()

      if (this.markers.length > 0) return
      try {
        const { data } = await api.get('/things/markers')
        this.markers = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching markers from DB', error)
      }
    },
    async updateMarker(updatedThing: Thing) {
      try {
        const index = this.markers.findIndex((t) => t.id === updatedThing.id)
        if (index !== -1) {
          this.markers[index] = {
            id: updatedThing.id,
            name: updatedThing.name,
            owners: updatedThing.owners,
            site_type: updatedThing.site_type,
            latitude: updatedThing.latitude,
            longitude: updatedThing.longitude,
            owns_thing: updatedThing.owns_thing,
            follows_thing: updatedThing.follows_thing,
            sampling_feature_code: updatedThing.sampling_feature_code,
          }
        }
      } catch (error) {
        console.error('Error updating marker in marker store', error)
      }
    },
    async removeMarker(thingId: string) {
      try {
        this.markers = this.markers.filter((thing) => thing.id !== thingId)
      } catch (error) {
        console.error('Error removing marker from marker store', error)
      }
    },
  },
})
