import { defineStore } from 'pinia'
import { useApiClient } from '@/utils/api-client'
import { Thing } from '@/types'

export const useThingStore = defineStore('things', {
  state: () => ({ things: {} as { [id: string]: Thing }, loaded: false }),
  getters: {},
  actions: {
    async fetchThingById(id: string) {
      const api = useApiClient()
      if (this.things[id]) return
      try {
        const { data } = await api.get(`/things/${id}`)
        this.things[id] = data
      } catch (error) {
        console.error('Error creating thing', error)
      }
    },
    async createThing(newThing: Thing) {
      const api = useApiClient()
      try {
        const { data } = await api.post(`/things/`, newThing)
        this.$patch({ things: { ...this.things, [data.id]: data } })
      } catch (error) {
        console.error('Error creating thing', error)
      }
    },
    async updateThing(updatedThing: Thing) {
      const api = useApiClient()
      try {
        await api.patch(`/things/${updatedThing.id}`, updatedThing)
        this.$patch({
          things: { ...this.things, [updatedThing.id]: updatedThing },
        })
      } catch (error) {
        console.error('Error updating thing', error)
      }
    },
    async updateThingFollowership(updatedThing: Thing) {
      const api = useApiClient()
      try {
        await api.patch(`/things/${updatedThing.id}/followership`)
        this.$patch({
          things: { ...this.things, [updatedThing.id]: updatedThing },
        })
      } catch (error) {
        console.error('Error updating thing followership', error)
      }
    },
    async deleteThing(thingId: string) {
      const api = useApiClient()
      try {
        await api.delete(`/things/${thingId}`)
        const newThings = { ...this.things }
        delete newThings[thingId]
        this.things = newThings
      } catch (error) {
        console.error('Error deleting thing', error)
      }
    },
  },
})
