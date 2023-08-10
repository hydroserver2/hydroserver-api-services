import { defineStore } from 'pinia'
import { Photo } from '@/types'

export const usePhotosStore = defineStore({
  id: 'photos',

  state: () => ({
    // Keyed by thingId
    photos: {} as Record<string, Array<Photo>>,
    loading: false,
  }),

  actions: {
    async fetchPhotos(thingId: string) {
      try {
        const response = await this.$http.get(`/photos/${thingId}`)
        if (response && response.status == 200) {
          this.photos[thingId] = response.data
        }
      } catch (error) {
        console.error('Error fetching photos from DB', error)
      }
    },

    async updatePhotos(
      thingId: string,
      newPhotos: File[],
      photosToDelete: string[]
    ) {
      try {
        this.loading = true
        const data = new FormData()
        newPhotos.forEach((photo) => data.append(`photos`, photo))
        photosToDelete.forEach((id) => data.append(`photosToDelete`, id))

        const response = await this.$http.post(`/photos/${thingId}`, data, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        if (response && response.status == 200) {
          this.photos[thingId] = response.data
        }
      } catch (error) {
        console.error('Error updating photos', error)
      } finally {
        this.loading = false
      }
    },
  },
})
