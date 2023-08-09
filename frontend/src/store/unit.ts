import { defineStore } from 'pinia'
import { Unit } from '@/types'

export const useUnitStore = defineStore('units', {
  state: () => ({ units: [] as Unit[], loaded: false }),
  getters: {
    ownedUnits(): Unit[] {
      return this.units.filter((u) => u.person_id != null)
    },
  },
  actions: {
    sortUnits() {
      this.units.sort((a, b) => a.name.localeCompare(b.name))
    },
    async fetchUnits() {
      if (this.units.length > 0) return
      try {
        const { data } = await this.$http.get('/units')
        this.units = data
        this.sortUnits()
        this.loaded = true
      } catch (error) {
        console.error('Error fetching units from DB', error)
      }
    },
    async createUnit(unit: Unit) {
      try {
        const { data } = await this.$http.post('/units', unit)
        this.units.push(data)
        this.sortUnits()
        return data
      } catch (error) {
        console.error('Error creating unit', error)
      }
    },
    async updateUnit(unit: Unit) {
      try {
        await this.$http.patch(`/units/${unit.id}`, unit)
        const index = this.units.findIndex((u) => u.id === unit.id)
        if (index !== -1) {
          this.units[index] = unit
        }
        this.sortUnits()
      } catch (error) {
        console.error('Error updating unit', error)
      }
    },
    async deleteUnit(unitId: string) {
      try {
        const response = await this.$http.delete(`/units/${unitId}`)
        if (response.status === 200 || response.status === 204) {
          this.units = this.units.filter((unit) => unit.id !== unitId)
          this.sortUnits()
        } else console.error('Error deleting unit from server', response)
      } catch (error) {
        console.error('Error deleting unit', error)
      }
    },
    getUnitById(id: string) {
      const unit = this.units.find((u) => u.id.toString() === id.toString())
      if (!unit) throw new Error(`Unit with id ${id} not found`)
      return unit
    },
    // async fetchUnitById(id: string) {
    //   try {
    //     const response = await this.$http.get(`/units/${id}`)
    //     if (response.status === 200) return response.data as Unit
    //   } catch (error) {
    //     console.error('Error deleting fetching unit by id', error)
    //   }
    // },
  },
})
