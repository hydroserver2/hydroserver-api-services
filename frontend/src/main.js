import {createApp} from 'vue';
import App from './App.vue';
import router from './router';
import store from './store'
import axios from 'axios'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
})

axios.defaults.baseURL = 'http://127.0.0.1:8000/api/';

// Axios interceptor for handling JWT tokens
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config;
  },
  (error) => Promise.reject(error)
)

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    const originalRequest = error.config
    if (error.response.status === 401 && !originalRequest._retry && error.response.data.detail === 'Unauthorized') {
      originalRequest._retry = true
      const refresh_token = localStorage.getItem('refresh_token')
      if (!refresh_token) {
        router.push('/login')
        return Promise.reject(error)
      }

      return axios.post('/token/refresh', {refresh_token: refresh_token})
      .then(response => {
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        originalRequest.headers['Authorization'] = `Bearer ${response.data.access_token}`
        return axios(originalRequest)
      })
      .catch(error => {
        // The refresh token is invalid
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        router.push('/login')
        return Promise.reject(error)
      })
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(router)
app.use(store)
app.use(vuetify)
app.mount('#app')

