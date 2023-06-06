import { defineStore } from 'pinia'
import router from '@/router/router'
import { User } from '@/types'
import Notification from './notifications'
import { useResetStore } from '@/store/resetStore'

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
      useResetStore().all()
      localStorage.clear()
    },
    async login(email: string, password: string) {
      try {
        this.loggingIn = true
        this.resetState()
        const response = await this.$http.post('/token', {
          email: email,
          password: password,
        })
        if (response.status === 401) {
          Notification.toast({
            message: 'Invalid email or password.',
          })
        } else if (response.status >= 500 && response.status < 600) {
          Notification.toast({
            message: 'Server error. Please try again later.',
          })
        } else {
          this.access_token = response.data.access_token
          this.refresh_token = response.data.refresh_token
          this.user = response.data.user
          await router.push({ name: 'Sites' })
          Notification.toast({ message: 'You have logged in!' })
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
          })
        } else {
          this.resetState()
          Notification.toast({
            message: 'Something went wrong',
          })
        }
        console.error('Error Logging in', error)
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
    async createUser(user: User) {
      try {
        const response = await this.$http.post('/user', user)
        if (response.status === 200) {
          Notification.toast({
            message: 'Account successfully created.',
          })
          await this.login(user.email, user.password)
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
          })
        } else {
          Notification.toast({
            message: 'Something went wrong.',
          })
        }
        console.error('Error creating user', error)
      }
    },
    async updateUser(user: User) {
      try {
        const { data } = await this.$http.patch('/user', user)
        this.user = data
      } catch (error) {}
    },
    async deleteAccount() {
      try {
        await this.$http.delete('/user')
        await this.logout()
        Notification.toast({ message: 'Your account has been deleted' })
      } catch (error) {
        console.error('Error deleting account:', error)
        Notification.toast({
          message:
            'Error occurred while deleting your account. Please try again.',
        })
      }
    },
  },
  getters: {
    isLoggedIn: (state) => {
      return !!state.access_token
    },
  },
})
