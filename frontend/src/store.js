import { createStore } from 'vuex';
import axios from 'axios'
import router from "./router.js";

const initialState = {
  access_token: null,
  refreshToken: null,
  loggingIn: false,
  loginError: null,
  things: [],
}

const store = createStore({
  state: {...initialState},
  mutations: {
    resetState: (state) => Object.assign(state, initialState),
    loginStart: state => state.loggingIn = true,
    loginStop: (state, errorMessage) => {
      state.loggingIn = false;
      state.loginError = errorMessage;
    },
    updateAccessToken: (state, access_token) => {
      state.access_token = access_token;
    },
    cacheProperty: (state, { key, data }) => {
      state[key] = data;
      localStorage.setItem(key, JSON.stringify(state[key]));
    },
    addThing(state, thing) {
      state.things.push(thing);
      localStorage.setItem('things', JSON.stringify(state.things));
    },
  },
  actions: {
    login({ commit }, loginData) {
      commit('loginStart');
      console.log("Logging in...")
      axios.post('/token', {
        ...loginData
      })
      .then(response => {
        // Data will be different for public vs logged-in users.
        // Clean up in case the user called any API endpoints before logging in
        commit('resetState')
        localStorage.clear()
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        commit('loginStop', null);
        commit('updateAccessToken', access_token);
        router.push({ name: 'Sites' }).catch((error) => {console.error('Error while navigating to Sites:', error);})
        console.log("Logged in")
      })
      .catch(error => {
        commit('loginStop', error.response);
        commit('updateAccessToken', null);
      })
    },
    async fetchOrGetFromCache({commit}, {key, apiEndpoint}) {
      const cachedData = localStorage.getItem(key);
      if (cachedData) {
        console.log(`Getting ${key} data from localStorage...`);
        commit('cacheProperty', {key, data: JSON.parse(cachedData)});
      } else {
        console.log(`Fetching ${key} data from API...`);
        try {
          const { data } = await axios.get(apiEndpoint);
          commit('cacheProperty', {key, data});
        } catch (error) {
          console.error(`Error fetching ${key} data from API`, error);
        }
      }
    },
    logout({commit}) {
      commit('resetState')
      localStorage.clear()
      router.push({ name: 'Home' }).catch((error) => {console.error('Error while navigating to Home:', error)});
    },
    fetchAccessToken({ commit }) {
      const access_token = localStorage.getItem('access_token');
      if (access_token) {
        commit('updateAccessToken', access_token);
      }
    },
  },
});

export default store;
