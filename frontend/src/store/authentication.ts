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
    user: new User(),
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
            type: 'error',
          })
        } else if (response.status >= 500 && response.status < 600) {
          Notification.toast({
            message: 'Server error. Please try again later.',
            type: 'error',
          })
        } else {
          this.access_token = response.data.access_token
          this.refresh_token = response.data.refresh_token
          this.user = response.data.user
          await router.push({ name: 'Sites' })
          Notification.toast({
            message: 'You have logged in!',
            type: 'success',
          })
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
            type: 'error',
          })
        } else {
          this.resetState()
          if (error.response.status === 401) {
            Notification.toast({
              message: 'Invalid email or password.',
              type: 'error',
            })
          } else {
            Notification.toast({
              message: 'Something went wrong',
              type: 'error',
            })
          }
        }
        console.error('Error Logging in', error)
      } finally {
        this.loggingIn = false
      }
    },
    async logout() {
      this.resetState()
      await router.push({ name: 'Login' })
      Notification.toast({ message: 'You have logged out', type: 'info' })
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
            type: 'success',
          })
          await this.login(user.email, user.password)
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
            type: 'error',
          })
        } else if (
          error.response.status === 400 &&
          error.response.data.detail === 'EmailAlreadyExists'
        ) {
          Notification.toast({
            message: 'A user with this email already exists.',
            type: 'error',
          })
        } else {
          Notification.toast({
            message: 'Something went wrong.',
            type: 'error',
          })
        }
        console.error('Error creating user', error)
      }
    },
    async updateUser(user: User) {
      try {
        const { data } = await this.$http.patch('/user', user)
        // things.organizations could be affected for many things so just invalidate cache
        useResetStore().things()
        this.user = data
      } catch (error) {}
    },
    async deleteAccount() {
      try {
        await this.$http.delete('/user')
        await this.logout()
        Notification.toast({
          message: 'Your account has been deleted',
          type: 'info',
        })
      } catch (error) {
        console.error('Error deleting account:', error)
        Notification.toast({
          message:
            'Error occurred while deleting your account. Please try again.',
          type: 'error',
        })
      }
    },
    async requestPasswordReset(email: String) {
      try {
        const response = await this.$http.post('/password_reset', {
          email: email,
        })
        return response.status === 200
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
            type: 'error',
          })
        } else if (error.response.status === 404) {
          Notification.toast({
            message: 'No account was found for the email you specified',
            type: 'error',
          })
        } else {
          Notification.toast({
            message:
              'Error occurred while requesting your password reset email. Please try again.',
            type: 'error',
          })
        }
        console.error('Error requesting password reset:', error)
        return false
      }
    },
    async resetPassword(uid: string, token: string, password: string) {
      try {
        const response = await this.$http.post('/reset_password', {
          uid: uid,
          token: token,
          password: password,
        })
        console.log('Reset Password Response', response)
        if (response.status === 200) {
          Notification.toast({
            message: 'Successfully reset password!',
            type: 'success',
          })
          await router.push({ name: 'Login' })
        }
      } catch (error: any) {
        if (!error.response) {
          Notification.toast({
            message: 'Network error. Please check your connection.',
            type: 'error',
          })
        } else {
          Notification.toast({
            message:
              'Error occurred while requesting your password reset email. Please try again.',
            type: 'error',
          })
        }
        console.error('Error requesting password reset:', error.response.status)
        return false
      }
    },
  },
  getters: {
    isLoggedIn: (state) => {
      return !!state.access_token
    },
  },
})
