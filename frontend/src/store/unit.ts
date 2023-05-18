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
    async createUnit(unit: Unit) {
      try {
        const { data } = await axios.post('/units', unit)
        this.units.push(data)
        return data
      } catch (error) {
        console.error('Error creating unit', error)
      }
    },
    async updateUnit(unit: Unit) {
      try {
        await axios.patch(`/units/${unit.id}`, unit)
        const index = this.units.findIndex((u) => u.id === unit.id)
        if (index !== -1) {
          this.units[index] = unit
        }
      } catch (error) {
        console.error('Error updating unit', error)
      }
    },
    async getUnitById(id: string) {
      const unit = this.units.find((u) => u.id.toString() === id.toString())
      if (!unit) throw new Error(`Unit with id ${id} not found`)
      return unit
    },
  },
})
