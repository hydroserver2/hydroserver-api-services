import { createStore } from 'vuex';
import axios from 'axios'
import router from "./router.js";

const store = createStore({
  state: {
    accessToken: null,
    refreshToken: null,
    loggingIn: false,
    loginError: null,
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
  },
  actions: {
    login({ commit }, loginData) {
      commit('loginStart');
      axios.post('http://127.0.0.1:8000/api/token', {
        ...loginData
      })
      .then(response => {
       const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        commit('loginStop', null);
        commit('updateAccessToken', access_token);
        router.push({ name: 'Sites' }).catch((error) => {console.error('Error while navigating to Sites:', error);});
      })
      .catch(error => {
        commit('loginStop', error.response.data.error);
        commit('updateAccessToken', null);
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
    }
  },
});

export default store;
