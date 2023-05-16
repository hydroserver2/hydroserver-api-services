import { defineStore } from 'pinia'
import axios from 'axios'
import { ProcessingLevel } from '@/types'

export const useProcessingLevelStore = defineStore('processingLevels', {
  state: () => ({ processingLevels: [] as ProcessingLevel[], loaded: false }),
  getters: {},
  actions: {
    async fetchDatastreams() {
      if (this.processingLevels.length > 0) return
      try {
        const { data } = await axios.get('/processing-levels')
        this.processingLevels = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching datastreams from DB', error)
      }
    },
  },
})
