import { createStore } from 'vuex';
import axios from 'axios'
import router from "./router.js";

const store = createStore({
  state: {
    accessToken: null,
    refreshToken: null,
    loggingIn: false,
    loginError: null,
    ownedThings: [],
    followedThings: [],
  },
  mutations: {
    loginStart: state => state.loggingIn = true,
    loginStop: (state, errorMessage) => {
      state.loggingIn = false;
      state.loginError = errorMessage;
    },
    updateAccessToken: (state, accessToken) => {
      state.accessToken = accessToken;
    },
    clearTokens: (state) => {
      state.accessToken = null;
      state.refreshToken = null;
    },
    cacheProperty: (state, { key, data }) => {
      state[key] = data;
      localStorage.setItem(key, JSON.stringify(state[key]));
    },
    addThing(state, thing) {
      state.ownedThings.push(thing);
      localStorage.setItem('ownedThings', JSON.stringify(state.ownedThings));
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
    fetchThings({commit}){
      const ownedThings = localStorage.getItem('ownedThings');
      const followedThings = localStorage.getItem('followedThings');
      if (ownedThings && followedThings) {
        console.log("Getting Site data from localStorage...")
        commit('cacheProperty',{ key: 'ownedThings', data: JSON.parse(ownedThings)});
        commit('cacheProperty',{ key: 'followedThings', data: JSON.parse(followedThings)});
      } else {
        store.dispatch('fetchUserData').catch((error) => {console.error('Error fetching user data from db', error);})
      }
    },
    fetchUserData({commit}) {
      axios.get('/user/data')
          .then(response => {
            console.log("Getting userData from DB...")
            console.log(response.data)
            commit('cacheProperty',{ key: 'ownedThings', data: response.data.owned_things });
            commit('cacheProperty',{ key: 'followedThings', data: response.data.followed_things });
          })
          .catch(error => {console.log(error)})
    },
    logout({commit}) {
      commit('clearTokens');
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
