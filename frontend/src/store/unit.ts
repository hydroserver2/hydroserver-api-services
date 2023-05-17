import { defineStore } from 'pinia'
import axios from 'axios'
import { Unit } from '@/types'

export const useUnitStore = defineStore('units', {
  state: () => ({ units: [] as Unit[], loaded: false }),
  getters: {
    ownedUnits(): Unit[] {
      return this.units.filter((u) => u.person_id != null)
    },
  },
  actions: {
    async fetchUnits() {
      if (this.units.length > 0) return
      try {
        const { data } = await axios.get('/units')
        this.units = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching units from DB', error)
      }
    },
  },
})
