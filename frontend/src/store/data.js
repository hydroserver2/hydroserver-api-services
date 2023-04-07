import { defineStore } from 'pinia';
import axios from 'axios';

export const useDataStore = defineStore({
  id: 'data',
  state: () => ({
    things: [],
  }),
  actions: {
    async fetchOrGetFromCache(key, apiEndpoint) {
      const cachedData = localStorage.getItem(key);
      if (cachedData) {
        console.log(`Getting ${key} data from localStorage...`);
        this.cacheProperty(key, JSON.parse(cachedData))
      } else {
        console.log(`Fetching ${key} data from API...`);
        try {
          const { data } = await axios.get(apiEndpoint);
          this.cacheProperty(key, data)
        } catch (error) {
          console.error(`Error fetching ${key} data from API`, error);
        }
      }
    },
    cacheProperty(key, data) {
      this[key] = data;
      localStorage.setItem(key, JSON.stringify(this[key]));
    },
    addThing(thing) {
      this.things.push(thing);
      localStorage.setItem('things', JSON.stringify(this.things));
    },
  },
});