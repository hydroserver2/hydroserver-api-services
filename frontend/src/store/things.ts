import { defineStore } from 'pinia'
import { Thing } from '@/types'

export const useThingStore = defineStore('things', {
  state: () => ({ things: {} as Record<string, Thing>, loaded: false }),
  getters: {
    ownedThings(): Thing[] {
      return Object.values(this.things).filter((thing) => thing.owns_thing)
    },
    followedThings(): Thing[] {
      return Object.values(this.things).filter((thing) => thing.follows_thing)
    },
    ownedOrFollowedThings(): Thing[] {
      return Object.values(this.things).filter(
        (thing) => thing.owns_thing || thing.follows_thing
      )
    },
  },
  actions: {
    async fetchThings() {
      if (this.loaded) return
      try {
        const { data } = await axios.get('/things')
        console.log('fetched things', data)
        const thingsDictionary = data.reduce(
          (acc: Record<string, Thing>, thing: Thing) => {
            acc[thing.id] = thing
            return acc
          },
          {} as Record<string, Thing>
        )
        this.$patch({ things: thingsDictionary, loaded: true })
      } catch (error) {
        console.error('Error fetching markers from DB', error)
      }
    },
    async fetchThingById(id: string) {
      if (this.things[id]) return
      console.log('fetching things from API')
      try {
        const { data } = await this.$http.get(`/things/${id}`)
        this.$patch({ things: { ...this.things, [id]: data } })
      } catch (error) {
        console.error('Error fetching thing', error)
      }
    },
    async createThing(newThing: Thing) {
      try {
        const { data } = await this.$http.post(`/things`, newThing)
        this.$patch({ things: { ...this.things, [data.id]: data } })
      } catch (error) {
        console.error('Error creating thing', error)
      }
    },
    async updateThing(updatedThing: Thing) {
      try {
        await this.$http.patch(`/things/${updatedThing.id}`, updatedThing)
        this.things[updatedThing.id] = updatedThing
      } catch (error) {
        console.error('Error updating thing', error)
      }
    },
    async updateThingFollowership(updatedThing: Thing) {
      try {
        await this.$http.patch(`/things/${updatedThing.id}/followership`)
        this.things[updatedThing.id] = updatedThing
      } catch (error) {
        console.error('Error updating thing followership', error)
      }
    },
    async deleteThing(thingId: string) {
      try {
        await this.$http.delete(`/things/${thingId}`)
        const newThings = { ...this.things }
        delete newThings[thingId]
        this.$patch({ things: newThings })
      } catch (error) {
        console.error('Error deleting thing', error)
      }
    },
  },
})
