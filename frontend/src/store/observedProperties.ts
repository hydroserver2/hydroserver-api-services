import { defineStore } from 'pinia'
import { ObservedProperty } from '@/types'

export const useObservedPropertyStore = defineStore('observedProperties', {
  state: () => ({
    observedProperties: [] as ObservedProperty[],
    loaded: false,
  }),
  getters: {
    ownedOP(): ObservedProperty[] {
      return this.observedProperties.filter((op) => op.person_id != null)
    },
    unownedOP(): ObservedProperty[] {
      return this.observedProperties.filter((op) => op.person_id == null)
    },
  },
  actions: {
    sortObservedProperties() {
      this.observedProperties.sort((a, b) => a.name.localeCompare(b.name))
    },
    async fetchObservedProperties() {
      if (this.observedProperties.length > 0) return
      try {
        const { data } = await this.$http.get('/observed-properties')
        this.observedProperties = data
        this.sortObservedProperties()
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
        this.sortObservedProperties()
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
        this.sortObservedProperties()
      } catch (error) {
        console.error('Error updating observed property', error)
      }
    },
    async deleteObservedProperty(id: string) {
      try {
        const response = await this.$http.delete(`/observed-properties/${id}`)
        if (response.status === 200 || response.status === 204) {
          this.observedProperties = this.observedProperties.filter(
            (op) => op.id !== id
          )
          this.sortObservedProperties()
        } else
          console.error(
            'Error deleting observed property from server',
            response
          )
      } catch (error) {
        console.error('Error deleting observed property', error)
      }
    },
    getById(id: string) {
      const op = this.observedProperties.find((op) => op.id === id)
      if (!op) throw new Error(`Observed Property with id ${id} not found`)
      return op
    },
  },
})
