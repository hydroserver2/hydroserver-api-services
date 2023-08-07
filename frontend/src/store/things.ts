import { defineStore } from 'pinia'
import { Thing, ThingMetadata } from '@/types'
import Notification from '@/store/notifications'

export const useThingStore = defineStore('things', {
  state: () => ({
    things: {} as Record<string, Thing>,
    POMetadata: {} as Record<string, ThingMetadata>,
    loaded: false,
  }),
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
    ownedOrFollowedThings(): Thing[] | any {
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
        return data
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
        const response = await this.$http.delete(`/things/${thingId}`)
        if (response && response.status == 200) {
          delete this.things[thingId]
        }
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
            type: 'success',
          })
        } else {
          Notification.toast({
            message: `${response.data.error}`,
            type: 'error',
          })
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
            type: 'error',
          })
        } else if (error.response.status === 404) {
          Notification.toast({
            message:
              'The email entered does not exist in our system. Please check your entry or use a different email.',
            type: 'error',
          })
        } else if (error.response.status == 422) {
          Notification.toast({
            message: `Specified user is already an owner of this site`,
            type: 'info',
          })
        } else if (error.response.status == 403) {
          if (error.response.data.error === 'NotPrimaryOwner')
            Notification.toast({
              message: `Only the primary owner can modify other users' ownership`,
              type: 'error',
            })
          else {
            Notification.toast({
              message: `Primary owner cannot edit their own ownership. Transfer ownership to another if you no longer wish to be the primary owner`,
              type: 'error',
            })
          }
        }
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
            type: 'success',
          })
        } else {
          Notification.toast({
            message: `${response.data.error}`,
            type: 'error',
          })
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
            type: 'error',
          })
        } else if (error.response.status === 404) {
          Notification.toast({
            message:
              'The email entered does not exist in our system. Please check your entry or use a different email.',
            type: 'error',
          })
        } else if (error.response.status == 403) {
          if (error.response.data.error === 'NotPrimaryOwner')
            Notification.toast({
              message: `Only the primary owner can modify other users' ownership`,
              type: 'error',
            })
          else {
            Notification.toast({
              message: `The specified email is already the primary owner of this site.`,
              type: 'error',
            })
          }
        }
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
            type: 'success',
          })
        } else {
          Notification.toast({
            message: `${response.data.error}`,
            type: 'error',
          })
        }
      } catch (error) {
        console.error('Error removing owner', error)
      }
    },
    async fetchPrimaryOwnerMetadataByThingId(id: string) {
      try {
        const response = await this.$http.get(`/things/${id}/metadata`)
        this.$patch({ POMetadata: { ...this.POMetadata, [id]: response.data } })
      } catch (error) {
        console.error('Error fetching primary owner data from DB', error)
      }
    },
  },
})
