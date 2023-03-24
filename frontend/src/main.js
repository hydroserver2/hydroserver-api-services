import {createApp} from 'vue';
import App from './App.vue';
import router from './router';
import store from './store'
import axios from 'axios'

axios.defaults.baseURL = 'http://127.0.0.1:8000/api/';

// Axios interceptor for handling JWT tokens
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')

