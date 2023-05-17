import { defineStore } from 'pinia'
import axios from 'axios'
import { Sensor } from '@/types'

export const useSensorStore = defineStore('sensor', {
  state: () => ({ sensors: [] as Sensor[], loaded: false }),
  getters: {},
  actions: {
    async fetchSensors() {
      if (this.sensors.length > 0) return
      try {
        const { data } = await axios.get('/sensors')
        this.sensors = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching units from DB', error)
      }
    },
  },
})
