import { defineStore } from 'pinia'
import axios from 'axios'
import { ObservedProperty } from '@/types'

export const useObservedPropertyStore = defineStore('observedProperties', {
  state: () => ({
    observedProperties: [] as ObservedProperty[],
    loaded: false,
  }),
  getters: {},
  actions: {
    async fetchObservedProperties() {
      if (this.observedProperties.length > 0) return
      try {
        const { data } = await axios.get('/observed-properties')
        this.observedProperties = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching observed properties from DB', error)
      }
    },
  },
})
