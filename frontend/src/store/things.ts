import { defineStore } from 'pinia'
import axios from 'axios'
import { Thing } from '@/types'

export const useThingStore = defineStore('things', {
  state: () => ({ things: {} as { [id: string]: Thing }, loaded: false }),
  getters: {},
  actions: {
    async fetchThingById(id: string) {
      if (this.things[id]) return
      try {
        const { data } = await axios.get(`/things/${id}`)
        this.things[id] = data
      } catch (error) {
        console.error('Error creating thing', error)
      }
    },
    async createThing(newThing: Thing) {
      try {
        const { data } = await axios.post(`/things/`, newThing)
        this.$patch({ things: { ...this.things, [data.id]: data } })
      } catch (error) {
        console.error('Error creating thing', error)
      }
    },
    async updateThing(updatedThing: Thing) {
      try {
        await axios.patch(`/things/${updatedThing.id}`, updatedThing)
        this.$patch({
          things: { ...this.things, [updatedThing.id]: updatedThing },
        })
      } catch (error) {
        console.error('Error updating thing', error)
      }
    },
    async updateThingFollowership(updatedThing: Thing) {
      try {
        await axios.patch(`/things/${updatedThing.id}/followership`)
        this.$patch({
          things: { ...this.things, [updatedThing.id]: updatedThing },
        })
      } catch (error) {
        console.error('Error updating thing followership', error)
      }
    },
    async deleteThing(thingId: string) {
      try {
        await axios.delete(`/things/${thingId}`)
        const newThings = { ...this.things }
        delete newThings[thingId]
        this.things = newThings
      } catch (error) {
        console.error('Error deleting thing', error)
      }
    },
  },
})
