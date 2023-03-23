import { createStore } from 'vuex';
import axios from 'axios'
import router from "./router.js";

const store = createStore({
  state: {
    accessToken: null,
    refreshToken: null,
    loggingIn: false,
    loginError: null,
    userData: null
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
    setUserData: (state, userData) => {
      state.userData = userData;
    }
  },
  actions: {
    login({ commit }, loginData) {
      commit('loginStart');
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
        store.dispatch('fetchUserData').catch((error) => {console.error('Error fetching user data from db', error);})
      })
      .catch(error => {
        commit('loginStop', error.response);
        commit('updateAccessToken', null);
      })
    },
    fetchUserData({commit}) {
      axios.get('/user/data')
        .then(response => {
          console.log(response.data)
          commit('setUserData', response.data);
        })
        .catch(error => {
          console.log(error);
        })
    },
    logout({commit}) {
      commit('clearTokens');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      router.push({ name: 'Home' })
          .catch((error) => {console.error('Error while navigating to Home:', error);});
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
