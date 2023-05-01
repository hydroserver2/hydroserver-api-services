import { defineStore } from 'pinia'

// TODO: circular dependency error because useAuthStore imports axios.config.ts
import axios from '@/plugins/axios.config'

import router from '@/router/router'

const initialState = () => ({
  access_token: null,
  refresh_token: null,
  loggingIn: false,
  loginError: null,
  things: [],
})

export const useAuthStore = defineStore({
  id: 'authentication',
  state: initialState,
  actions: {
    resetState() {
      Object.assign(this, initialState())
    },
    async login(loginData) {
      try {
        this.loggingIn = true
        this.resetState()
        localStorage.clear()

        const response = await axios.post('/token', { ...loginData })
        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        this.access_token = access_token
        this.refresh_token = refresh_token

        await router.push({ name: 'Sites' })
      } catch (error) {
        this.logout()
      } finally {
        this.loggingIn = false
      }
    },
    logout() {
      this.resetState()
      localStorage.clear()
      router.push({ name: 'Home' }).catch((error) => {
        console.error('Error while navigating to Home:', error)
      })
    },
    fetchAccessToken() {
      const access_token = localStorage.getItem('access_token')
      if (access_token) this.access_token = access_token
      const refresh_token = localStorage.getItem('refresh_token')
      if (refresh_token) this.refresh_token = refresh_token
    },
    async refreshAccessToken() {
      console.log('Access token expired. refreshing token...')
      try {
        const response = await axios.post('/token/refresh', {
          refresh_token: this.refresh_token,
        })
        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        this.access_token = access_token
        localStorage.setItem('refresh_token', refresh_token)
        this.refresh_token = refresh_token
        console.log('Access token refreshed')
      } catch (error) {
        console.error('Error refreshing access token:', error)
        this.logout()
      }
    },
  },
})
