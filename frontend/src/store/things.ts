import { defineStore } from 'pinia'
import { Thing } from '@/types'
import Notification from '@/store/notifications'

export const useThingStore = defineStore('things', {
  state: () => ({ things: {} as Record<string, Thing>, loaded: false }),
  getters: {
    primaryOwnedThings(): Thing[] {
      return Object.values(this.things).filter(
        (thing) => thing.is_primary_owner
      )
    },
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
        const { data } = await this.$http.get('/things')
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
        console.error('Error fetching things from DB', error)
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
        const response = await this.$http.patch(
          `/things/${updatedThing.id}`,
          updatedThing
        )
        if (response && response.status == 200) {
          this.things[updatedThing.id] = response.data as Thing
        }
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
    async updateThingPrivacy(thingId: string, thingPrivacy: boolean) {
      try {
        const response = await this.$http.patch(`/things/${thingId}/privacy`, {
          is_private: thingPrivacy,
        })
        if (response && response.status == 200) {
          this.things[thingId] = response.data as Thing
        }
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
    async addSecondaryOwner(thingId: string, email: string) {
      try {
        const response = await this.$http.patch(
          `/things/${thingId}/ownership`,
          {
            email: email,
            make_owner: true,
          }
        )
        if (response && response.status == 200) {
          this.things[thingId] = response.data
          Notification.toast({
            message: `Successfully added secondary owner!`,
          })
        } else {
          Notification.toast({
            message: `${response.data.error}`,
          })
        }
      } catch (error) {
        console.error('Error adding secondary owner', error)
      }
    },
    async transferPrimaryOwnership(thingId: string, email: string) {
      try {
        const response = await this.$http.patch(
          `/things/${thingId}/ownership`,
          {
            email: email,
            transfer_primary: true,
          }
        )
        if (response && response.status == 200) {
          this.things[thingId] = response.data
          Notification.toast({
            message: `Successfully transferred ownership!`,
          })
        } else {
          Notification.toast({
            message: `${response.data.error}`,
          })
        }
      } catch (error) {
        console.error('Error transferring primary ownership', error)
      }
    },
    async removeOwner(thingId: string, email: string) {
      try {
        const response = await this.$http.patch(
          `/things/${thingId}/ownership`,
          {
            email: email,
            remove_owner: true,
          }
        )
        if (response && response.status == 200) {
          this.things[thingId] = response.data
          Notification.toast({
            message: `Successfully removed owner`,
          })
        } else {
          Notification.toast({
            message: `${response.data.error}`,
          })
        }
      } catch (error) {
        console.error('Error removing owner', error)
      }
    },
  },
})
