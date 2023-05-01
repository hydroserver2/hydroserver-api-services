import { defineStore } from 'pinia'
import axios from '@/plugins/axios.config'

export const useDataStore = defineStore({
  id: 'data',
  state: () => ({
    things: [],
    sensors: [],
    observedProperties: [],
    units: [],
    processingLevels: [],
    datastreams: [],
    user: {},
  }),
  actions: {
    async fetchOrGetFromCache(key, apiEndpoint) {
      const cachedData = localStorage.getItem(key)
      if (cachedData) {
        // console.log(`Getting ${key} data from localStorage...`);
        this.cacheProperty(key, JSON.parse(cachedData))
      } else {
        // console.log(`Fetching ${key} data from API...`);
        try {
          const { data } = await axios.get(apiEndpoint)
          this.cacheProperty(key, data)
        } catch (error) {
          console.error(`Error fetching ${key} data from API`, error)
        }
      }
    },
    cacheProperty(key, data) {
      this[key] = data
      localStorage.setItem(key, JSON.stringify(this[key]))
    },
    addThing(thing) {
      this.things.push(thing)
      localStorage.setItem('things', JSON.stringify(this.things))
    },
    addSensor(sensor) {
      this.sensors.push(sensor)
      localStorage.setItem('sensors', JSON.stringify(this.sensors))
    },
    addObservedProperty(observedProperty) {
      this.observedProperties.push(observedProperty)
      localStorage.setItem(
        'observedProperties',
        JSON.stringify(this.observedProperties)
      )
    },
    addUnit(unit) {
      this.units.push(unit)
      localStorage.setItem('units', JSON.stringify(this.units))
    },
    addProcessingLevel(processingLevel) {
      this.processingLevels.push(processingLevel)
      localStorage.setItem(
        'processingLevels',
        JSON.stringify(this.processingLevels)
      )
    },
    addDatastream(datastream) {
      this.datastreams.push(datastream)
      localStorage.setItem('datastreams', JSON.stringify(this.datastreams))
    },
  },
})
