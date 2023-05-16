import { defineStore } from 'pinia'
import axios from 'axios'
import { Datastream } from '@/types'

export const useDatastreamStore = defineStore('datastreams', {
  state: () => ({
    datastreams: {} as Record<string, Datastream[]>,
    loaded: false,
  }),
  getters: {},
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
  },
})
