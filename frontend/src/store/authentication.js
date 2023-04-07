import { defineStore } from 'pinia';
import axios from 'axios';
import router from '@/router';

const initialState = () => ({
  access_token: null,
  refreshToken: null,
  loggingIn: false,
  loginError: null,
  things: [],
});

export const useAuthStore = defineStore({
  id: 'authentication',
  state: initialState,
  actions: {
    resetState() { Object.assign(this, initialState()) },
    loginStart() { this.loggingIn = true },
    loginStop(errorMessage) {
      this.loggingIn = false;
      this.loginError = errorMessage;
    },
    updateAccessToken(access_token) {
      this.access_token = access_token;
    },
    async login(loginData) {
      this.loginStart();
      console.log('Logging in...');
      try {
        const response = await axios.post('/token', {
          ...loginData,
        });
        this.resetState();
        localStorage.clear();
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        this.loginStop(null);
        this.updateAccessToken(access_token);
        router.push({ name: 'Sites' }).catch((error) => {
          console.error('Error while navigating to Sites:', error);
        });
        console.log('Logged in');
      } catch (error) {
        this.loginStop(error.response);
        this.updateAccessToken(null);
      }
    },
    logout() {
      this.resetState();
      localStorage.clear();
      router.push({ name: 'Home' }).catch((error) => {
        console.error('Error while navigating to Home:', error);
      });
    },
    fetchAccessToken() {
      const access_token = localStorage.getItem('access_token');
      if (access_token) {
        this.updateAccessToken(access_token);
      }
    },
  },
});
