import { defineStore } from 'pinia'
import router from '@/router/router'
import { User } from '@/types'
import { Subject } from 'rxjs'
import Notification from './notifications'
import { useResetStore } from '@/store/resetStore'

export const useAuthStore = defineStore({
  id: 'authentication',
  state: () => ({
    access_token: '',
    refresh_token: '',
    user: new User(),
    loggingIn: false,
    sendingVerificationEmail: false,
    isLoginListenerSet: false,
    loggedIn$: new Subject<void>(),
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
        const tokenResponse = await this.$http.post('/account/jwt/pair', {
          email: email,
          password: password,
        })
        if (tokenResponse.status === 200) {
          this.access_token = tokenResponse.data.access
          this.refresh_token = tokenResponse.data.refresh
          const userResponse = await this.$http.get('/account/user')
          if (userResponse.status === 200) {
            this.user = userResponse.data
            await router.push({ name: 'Sites' })
            Notification.toast({
              message: 'You have logged in!',
              type: 'success',
            })
          } else if (userResponse.status === 401) {
            Notification.toast({
              message: 'Invalid email or password.',
              type: 'error',
            })
          } else {
            Notification.toast({
              message: 'Server error. Please try again later.',
              type: 'error',
            })
          }
        } else if (tokenResponse.status === 401) {
          Notification.toast({
            message: 'Invalid email or password.',
            type: 'error',
          })
        } else {
          Notification.toast({
            message: 'Server error. Please try again later.',
            type: 'error',
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
      await router.push({ name: 'Login' })
      this.resetState()
    },
    async refreshAccessToken() {
      try {
        const { data } = await this.$http.post('/account/jwt/refresh', {
          refresh: this.refresh_token,
        })
        this.access_token = data.access
        this.refresh_token = data.refresh
        console.log('Access token refreshed')
      } catch (error) {
        console.error('Error refreshing access token:', error)
        await this.logout()
      }
    },
    async createUser(user: User) {
      try {
        const response = await this.$http.post('/account/user', user)
        if (response.status === 200) {
          try {
            useResetStore().things()
          } catch (error) {}
          this.user = response.data.user
          this.access_token = response.data.access
          this.refresh_token = response.data.refresh
          await router.push({ name: 'VerifyEmail' })
          Notification.toast({
            message: 'Account successfully created.',
            type: 'success',
          })
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
    async sendVerificationEmail() {
      if (this.sendingVerificationEmail === true) { return }
      this.sendingVerificationEmail = true
      const response = await this.$http.post('/account/send-verification-email')
      this.sendingVerificationEmail = false
      if (response.status === 200) {
        Notification.toast({
          message: 'Verification email sent successfully.',
          type: 'info',
        })
      } else {
        Notification.toast({
          message: 'Failed to send verification email.',
          type: 'error',
        })
      }
    },
    async activateAccount(uid: string, token: string) {
      const response = await this.$http.post('account/activate', {
        uid: uid,
        token: token
      })
      if (response.status === 200 && response.data.user.is_verified) {
        this.user = response.data.user
        this.access_token = response.data.access
        this.refresh_token = response.data.refresh
        Notification.toast({
          message: 'Your HydroServer account has been activated.',
          type: 'success',
        })
      } else {
        Notification.toast({
          message: 'Account activation failed. Token incorrect or expired.',
          type: 'error',
        })
      }
      await router.push({ name: 'Sites' })
    },
    async updateUser(user: User) {
      try {
        const { data } = await this.$http.patch('/account/user', user)
        // things.organizations could be affected for many things so just invalidate cache
        try {
          useResetStore().things()
        } catch (error) {}
        this.user = data
      } catch (error) {}
    },
    async deleteAccount() {
      try {
        await this.$http.delete('/account/user')
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
        const response = await this.$http.post('/user/password_reset', {
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
        const response = await this.$http.post('/user/reset_password', {
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
    async OAuthLogin(backend: string, callback?: () => any) {
      let OAuthUrl: string = ''

      if (backend === 'google') {
        OAuthUrl = '/api/account/google/login'
      } else if (backend === 'orcid') {
        OAuthUrl = '/api/account/orcid/login'
      }

      window.open(OAuthUrl, '_blank')

      this.isLoginListenerSet = false

      if (!this.isLoginListenerSet) {
        this.isLoginListenerSet = true // Prevents registering the listener more than once
        console.info(`User: listening to login window...`)
        window.addEventListener('message', async (event: MessageEvent) => {
          console.log(event)
          if (
            // event.origin !== APP_URL ||
            !event.data.hasOwnProperty('access')
          ) {
            return
          }

          if (event.data.access) {
            console.log(event)

            this.access_token = event.data.access
            this.refresh_token = event.data.refresh
            this.user = event.data.user
            await router.push({ name: 'Sites' })

            Notification.toast({
              message: 'You have logged in!',
              type: 'success',
            })
            // await User.commit((state) => {
            //   state.isLoggedIn = true
            //   state.accessToken = event.data.accessToken
            // })
            this.loggedIn$.next()
            this.isLoginListenerSet = false
            callback?.()
          } else {
            Notification.toast({
              message: 'Failed to Log In',
              type: 'error',
            })
          }
        })
      }
    },
  },
  getters: {
    isLoggedIn: (state) => {
      return !!state.access_token
    },
    isVerified: (state) => {
      return state.user.is_verified
    }
  },
})