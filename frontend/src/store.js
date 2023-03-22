import { createStore } from 'vuex';

const store = createStore({
  state: {
    accessToken: null,
    refreshToken: null,
  },
  mutations: {
    setAccessToken(state, accessToken) {
      console.log('setAccessToken:', accessToken);
      state.accessToken = accessToken;
      localStorage.setItem('access_token', accessToken);
    },
    setRefreshToken(state, refreshToken) {
      console.log('setRefreshToken:', refreshToken);
      state.refreshToken = refreshToken;
      localStorage.setItem('refresh_token', refreshToken);
    },
    clearTokens(state) {
      state.accessToken = null;
      state.refreshToken = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
  actions: {
    loadTokens({ commit }) {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      console.log('loadTokens:', accessToken, refreshToken);
      commit('setAccessToken', localStorage.getItem('access_token'));
      commit('setRefreshToken', localStorage.getItem('refresh_token'));
    },
  },
  getters: {
    isAuthenticated: ({ accessToken }) => accessToken !== null,
  },
});

export default store;
