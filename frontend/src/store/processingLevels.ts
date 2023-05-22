import { defineStore } from 'pinia'
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
        const { data } = await this.$http.get('/processing-levels')
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
        const { data } = await this.$http.patch(
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
        const { data } = await this.$http.post(
          '/processing-levels',
          processingLevel
        )
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
        const response = await this.$http.delete(`/processing-levels/${id}`)
        if (response.status === 200 || response.status === 204)
          this.processingLevels = this.processingLevels.filter(
            (pl) => pl.id !== id
          )
        else
          console.error('Error deleting processing level from server', response)
      } catch (error) {
        console.error('Error deleting processing level', error)
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
