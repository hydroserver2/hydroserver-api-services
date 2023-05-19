import { defineStore } from 'pinia'
import { ObservedProperty } from '@/types'
import { useApiClient } from '@/utils/api-client'

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
        const { data } = await this.$http.get('/observed-properties')
        this.observedProperties = data
        this.loaded = true
      } catch (error) {
        console.error('Error fetching observed properties from DB', error)
      }
    },
    async createObservedProperty(observedProperty: ObservedProperty) {
      try {
        const { data } = await this.$http.post(
          '/observed-properties',
          observedProperty
        )
        this.observedProperties.push(data)
        return data
      } catch (error) {
        console.error('Error creating observed property', error)
      }
    },
    async updateObservedProperty(observedProperty: ObservedProperty) {
      try {
        await this.$http.patch(
          `/observed-properties/${observedProperty.id}`,
          observedProperty
        )
        const index = this.observedProperties.findIndex(
          (op) => op.id === observedProperty.id
        )
        if (index !== -1) {
          this.observedProperties[index] = observedProperty
        }
      } catch (error) {
        console.error('Error updating observed property', error)
      }
    },
    getById(id: string) {
      const op = this.observedProperties.find((op) => op.id === id)
      if (!op) throw new Error(`Observed Property with id ${id} not found`)
      return op
    },
  },
})
