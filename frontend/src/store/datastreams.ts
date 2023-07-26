import { defineStore } from 'pinia'
import { Datastream } from '@/types'

export const useDatastreamStore = defineStore('datastreams', {
  state: () => ({
    datastreams: {} as Record<string, Datastream[]>,
    loaded: false,
  }),
  getters: {
    getDatastreamsByParameter:
      (state) =>
      (parameter_name: keyof Datastream, parameter_id: string | number) => {
        const datastreams = Object.values(state.datastreams).flat()
        return datastreams.filter((ds) => ds[parameter_name] === parameter_id)
      },
    primaryOwnedDatastreams: (state) => {
      const allDatastreams = Object.values(state.datastreams).flat()
      return allDatastreams.filter((ds) => ds.is_primary_owner)
    },
  },
  actions: {
    async fetchDatastreams() {
      try {
        const { data } = await this.$http.get('/datastreams')
        let newDatastreams: Record<string, Datastream[]> = {}
        data.forEach((datastream: Datastream) => {
          if (!newDatastreams[datastream.thing_id]) {
            newDatastreams[datastream.thing_id] = []
          }
          newDatastreams[datastream.thing_id].push(datastream)
        })
        this.$patch({ datastreams: newDatastreams })
        this.loaded = true
      } catch (error) {
        console.error('Error fetching datastreams from DB', error)
      }
    },
    async fetchDatastreamsByThingId(id: string) {
      if (this.datastreams[id]) return
      try {
        const { data } = await this.$http.get(`/datastreams/${id}`)
        this.datastreams[id] = data
      } catch (error) {
        console.error(
          `Error fetching datastreams for thing with id ${id} from DB`,
          error
        )
      }
    },
    async updateDatastream(datastream: Datastream) {
      try {
        const { data } = await this.$http.patch(
          `/datastreams/patch/${datastream.id}`,
          datastream
        )
        const datastreamsForThing = this.datastreams[data.thing_id]
        const index = datastreamsForThing.findIndex((ds) => ds.id === data.id)
        if (index !== -1) datastreamsForThing[index] = data
      } catch (error) {
        console.error('Error updating datastream', error)
      }
    },
    async createDatastream(newDatastream: Datastream) {
      try {
        const { data } = await this.$http.post(
          `/datastreams/${newDatastream.thing_id}`,
          newDatastream
        )
        if (!this.datastreams[newDatastream.thing_id]) {
          this.datastreams[newDatastream.thing_id] = []
        }
        this.datastreams[newDatastream.thing_id].push(data)
      } catch (error) {
        console.error('Error creating datastream', error)
      }
    },
    async deleteDatastream(id: string, thingId: string) {
      try {
        const response = await this.$http.delete(`/datastreams/${id}/temp`)
        if (response && response.status == 200) {
          const datastreams = this.datastreams[thingId].filter(
            (datastream) => datastream.id !== id
          )
          this.$patch({
            datastreams: { ...this.datastreams, [thingId]: datastreams },
          })
        }
      } catch (error) {
        console.error(`Error deleting datastream with id ${id}`, error)
      }
    },
    async setVisibility(id: string, visibility: boolean) {
      try {
        const { data } = await this.$http.patch(`/datastreams/patch/${id}`, {
          is_visible: visibility,
        })
        const datastreamIndex = this.datastreams[data.thing_id].findIndex(
          (ds) => ds.id === id
        )
        if (datastreamIndex !== -1)
          this.datastreams[data.thing_id][datastreamIndex] = data
        else {
          console.error(
            `Datastream with id ${id} not found in the datastreams list`
          )
        }
      } catch (error) {
        console.error(
          `Error toggling visibility for datastream with id ${id}`,
          error
        )
      }
    },
    getDatastreamForThingById(
      thingId: string,
      datastreamId: string
    ): Datastream | null {
      const thingDatastreams = this.datastreams[thingId]
      if (thingDatastreams) {
        const datastream = thingDatastreams.find((ds) => ds.id === datastreamId)
        return datastream ? datastream : null
      }
      return null
    },
    getDatastreamById(datastreamId: string): Datastream | null {
      for (const thingId in this.datastreams) {
        const thingDatastreams = this.datastreams[thingId]
        const datastream = thingDatastreams.find((ds) => ds.id === datastreamId)
        if (datastream) {
          return datastream
        }
      }
      return null
    },
  },
})
