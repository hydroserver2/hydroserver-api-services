import { defineStore } from 'pinia'
import axios from 'axios'
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
        console.log('by param', state.datastreams)
        return datastreams.filter((ds) => ds[parameter_name] === parameter_id)
      },
  },
  actions: {
    async fetchDatastreams() {
      if (this.loaded) return
      try {
        const { data } = await axios.get('/datastreams')
        data.forEach((datastream: Datastream) => {
          if (!this.datastreams[datastream.thing_id]) {
            this.datastreams[datastream.thing_id] = []
          }
          this.datastreams[datastream.thing_id].push(datastream)
        })
        this.loaded = true
      } catch (error) {
        console.error('Error fetching datastreams from DB', error)
      }
    },
    async fetchDatastreamsByThingId(id: string) {
      if (this.datastreams[id]) return
      try {
        const { data } = await axios.get(`/datastreams/${id}`)
        this.datastreams[id] = data
      } catch (error) {
        console.error(
          `Error fetching datastreams for thing with id ${id} from DB`,
          error
        )
      }
    },
    async updateDatastream(updatedDatastream: Datastream) {
      try {
        await axios.patch(
          `/datastreams/${updatedDatastream.id}`,
          updatedDatastream
        )
        const datastreamsForThing = this.datastreams[updatedDatastream.thing_id]
        const index = datastreamsForThing.findIndex(
          (ds) => ds.id === updatedDatastream.id
        )
        if (index !== -1) datastreamsForThing[index] = updatedDatastream
      } catch (error) {
        console.error('Error updating datastream', error)
      }
    },
    async createDatastream(newDatastream: Datastream) {
      try {
        const { data } = await axios.post(`/datastreams/`, newDatastream)
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
        await axios.delete(`/datastreams/${id}`)
        const datastreams = this.datastreams[thingId].filter(
          (datastream) => datastream.id !== id
        )
        this.$patch({
          datastreams: { ...this.datastreams, [thingId]: datastreams },
        })
      } catch (error) {
        console.error(`Error deleting datastream with id ${id}`, error)
      }
    },
    async setVisibility(id: string, visibility: boolean) {
      try {
        const { data } = await axios.patch(`/datastreams/${id}`, {
          is_visible: visibility,
        })
        const datastreamIndex = this.datastreams[data.thing_id].findIndex(
          (ds) => ds.id === id
        )
        if (datastreamIndex !== -1) {
          this.datastreams[data.thing_id][datastreamIndex] = data
        } else {
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
    getDatastreamById(
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
  },
})
