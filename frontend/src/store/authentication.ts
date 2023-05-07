import { defineStore } from 'pinia'
import apiClient from '@/utils/common-https'
import router from '@/router/router'
import Notification from './notifications'

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
    async login(loginData: any) {
      try {
        this.loggingIn = true
        this.resetState()
        localStorage.clear()

        const response = await apiClient.post('/token', { ...loginData })

        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        this.access_token = access_token
        this.refresh_token = refresh_token
        Notification.toast({ message: 'You have logged in!' })
        router.push({ name: 'Sites' })
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
      Notification.toast({ message: 'You have logged out' })
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
        const response = await apiClient.post('/token/refresh', {
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
  getters: {
    isLoggedIn: (state) => {
      return !!state.access_token
    },
  },
})
