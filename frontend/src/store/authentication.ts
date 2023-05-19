import { defineStore } from 'pinia'
import router from '@/router/router'
import { User } from '@/types'
import Notification from './notifications'

export const useAuthStore = defineStore({
  id: 'authentication',
  state: () => ({
  access_token: '',
  refresh_token: '',
    user: {
    id: '',
    email: '',
    first_name: '',
    middle_name: '',
    last_name: '',
    phone: '',
    address: '',
    organization: '',
    type: '',
  },
    loggingIn: false,
  }),
  actions: {
    resetState() {
      this.$reset()
      localStorage.clear()
    },
    async login(email: string, password: string) {
      try {
        this.loggingIn = true
        this.resetState()
        const { data } = await this.$http.post('/token', {
          email: email,
          password: password,
        })
        this.access_token = data.access_token
        this.refresh_token = data.refresh_token
        this.user = data.user
        await router.push({ name: 'Sites' })
        Notification.toast({ message: 'You have logged in!' })
      } catch (error) {
        await this.logout()
      } finally {
        this.loggingIn = false
      }
    },
    async logout() {
      this.resetState()
      await router.push({ name: 'Home' })
      Notification.toast({ message: 'You have logged out' })
    },
    async refreshAccessToken() {
      try {
        const { data } = await this.$http.post('/token/refresh', {
          refresh_token: this.refresh_token,
        })
        this.access_token = data.access_token
        this.refresh_token = data.refresh_token
        console.log('Access token refreshed')
      } catch (error) {
        console.error('Error refreshing access token:', error)
        await this.logout()
      }
    },
    async updateUser(user: User) {
      try {
        const { data } = await this.$http.patch('/user', user)
        this.user = data
      } catch (error) {}
    },
  },
  getters: {
    isLoggedIn: (state) => {
      return !!state.access_token
    },
  },
})
