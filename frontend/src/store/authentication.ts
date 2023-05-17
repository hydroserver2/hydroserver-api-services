import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router/router'
import { User } from '@/types'

const initialState = () => ({
  access_token: null,
  refresh_token: null,
  user: null as User | null,
  loggingIn: false,
})

export const useAuthStore = defineStore({
  id: 'authentication',
  state: initialState,
  actions: {
    resetState() {
      Object.assign(this, initialState())
      localStorage.clear()
    },
    async login(email: string, password: string) {
      try {
        this.loggingIn = true
        this.resetState()
        const { data } = await axios.post('/token', {
          email: email,
          password: password,
        })
        this.access_token = data.access_token
        this.refresh_token = data.refresh_token
        this.user = data.user
        await router.push({ name: 'Sites' })
      } catch (error) {
        await this.logout()
      } finally {
        this.loggingIn = false
      }
    },
    async logout() {
      this.resetState()
      await router.push({ name: 'Home' })
    },
    async refreshAccessToken() {
      try {
        const { data } = await axios.post('/token/refresh', {
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
        const { data } = await axios.patch('/user', user)
        this.user = data
      } catch (error) {}
    },
  },
})
