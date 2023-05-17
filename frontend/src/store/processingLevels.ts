import { defineStore } from 'pinia'
import axios from 'axios'
import { ProcessingLevel } from '@/types'

export const useProcessingLevelStore = defineStore('processingLevels', {
  state: () => ({ processingLevels: [] as ProcessingLevel[], loaded: false }),
  getters: {
    ownedProcessingLevels(): ProcessingLevel[] {
      return this.processingLevels.filter((pl) => pl.person_id != null)
    },
  },
  actions: {
    async fetchProcessingLevels() {
      if (this.loaded) return
      try {
        const { data } = await axios.get('/processing-levels')
        this.processingLevels = data.sort(
          (a: ProcessingLevel, b: ProcessingLevel) =>
            a.processing_level_code.localeCompare(b.processing_level_code)
        )
        this.loaded = true
      } catch (error) {
        console.error('Error fetching processing levels from DB', error)
      }
    },
    async updateProcessingLevel(processingLevel: ProcessingLevel) {
      try {
        const { data } = await axios.patch(
          `/processing-levels/${processingLevel.id}`,
          processingLevel
        )
        const index = this.processingLevels.findIndex(
          (pl) => pl.id === processingLevel.id
        )
        if (index !== -1) this.processingLevels[index] = data
      } catch (error) {
        console.error(
          `Error updating processing level with id ${processingLevel.id}`,
          error
        )
      }
    },
    async createProcessingLevel(processingLevel: ProcessingLevel) {
      try {
        const { data } = await axios.post('/processing-levels', processingLevel)
        this.processingLevels.push(data)
        this.processingLevels = this.processingLevels.sort(
          (a: ProcessingLevel, b: ProcessingLevel) =>
            a.processing_level_code.localeCompare(b.processing_level_code)
        )
        return data
      } catch (error) {
        console.error('Error creating processing level', error)
      }
    },
    async deleteProcessingLevel(id: string) {
      try {
        await axios.delete(`/processing-levels/${id}`)
        this.processingLevels = this.processingLevels.filter(
          (pl) => pl.id !== id
        )
      } catch (error) {
        console.error(`Error deleting processing level with id ${id}`, error)
      }
    },
    async getProcessingLevelById(id: string) {
      if (!this.loaded) await this.fetchProcessingLevels()

      const processingLevel = this.processingLevels.find((pl) => pl.id === id)

      if (!processingLevel)
        throw new Error(`Processing Level with id ${id} not found`)

      return processingLevel
    },
  },
})
