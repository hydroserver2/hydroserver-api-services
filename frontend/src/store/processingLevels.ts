import { defineStore } from 'pinia'
import { ProcessingLevel } from '@/types'
import { useApiClient } from '@/utils/api-client'

export const useProcessingLevelStore = defineStore('processingLevels', {
  state: () => ({ processingLevels: [] as ProcessingLevel[], loaded: false }),
  getters: {
    ownedProcessingLevels(): ProcessingLevel[] {
      return this.processingLevels.filter((pl) => pl.person_id != null)
    },
  },
  actions: {
    async fetchProcessingLevels() {
      const api = useApiClient()
      if (this.loaded) return
      try {
        const { data } = await api.get('/processing-levels')
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
      const api = useApiClient()
      try {
        const { data } = await api.patch(
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
      const api = useApiClient()
      try {
        const { data } = await api.post('/processing-levels', processingLevel)
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
      const api = useApiClient()
      try {
        await api.delete(`/processing-levels/${id}`)
        this.processingLevels = this.processingLevels.filter(
          (pl) => pl.id !== id
        )
      } catch (error) {
        console.error(`Error deleting processing level with id ${id}`, error)
      }
    },
    async getProcessingLevelById(id: string) {
      await this.fetchProcessingLevels()
      const processingLevel = this.processingLevels.find(
        (pl) => pl.id.toString() === id.toString()
      )

      if (!processingLevel)
        throw new Error(`Processing Level with id ${id} not found`)

      return processingLevel
    },
  },
})
