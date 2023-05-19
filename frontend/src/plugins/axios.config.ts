import { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { AxiosResponse } from 'axios'
import http from '@/utils/common-https'
import router from '@/router/router'
import { useAuthStore } from '@/store/authentication'
import type { App } from 'vue'

let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token = '') => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error)
    else prom.resolve(token)
  })
  failedQueue = []
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $http: AxiosInstance
  }
}

export default {
  install: (app: App): void => {
    app.config.globalProperties.$http = http
    const $http = app.config.globalProperties.$http

    // Axios interceptor for handling JWT tokens
    const handleRequest = async (config: InternalAxiosRequestConfig) => {
      const authStore = useAuthStore()
      if (authStore.access_token)
        config.headers.Authorization = `Bearer ${authStore.access_token}`

      if (authStore.refresh_token)
        config.headers.Refresh_Authorization = `Bearer ${authStore.refresh_token}`
      return config
    }

    const handleRequestError = async (error: AxiosError) => {
      if (
        error.response?.status === 401 &&
        error.config?.url === '/token/refresh'
      ) {
        const authStore = useAuthStore()
        console.log('Refresh Token has failed. Redirecting to login page...')
        await authStore.logout()
        await router.push('/login')
        return Promise.reject(error)
      }
    }

    const handleResponse = (response: AxiosResponse) => {
      return response
    }

    const handleResponseError = async (error: AxiosError) => {
      const originalRequest:
        | (InternalAxiosRequestConfig<any> & { _retry?: boolean })
        | undefined = error.config
      const authStore = useAuthStore()

      if (originalRequest) {
        if (
          error.response?.status === 401 &&
          originalRequest.url === '/token/refresh'
        ) {
          console.log('Refresh Token has failed. Redirecting to login page...')
          authStore.logout()
          await router.push('/login')
          return Promise.reject(error)
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject })
            })
              .then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`
                return $http(originalRequest)
              })
              .catch((err) => Promise.reject(err))
          }

          originalRequest._retry = true
          isRefreshing = true

          try {
            await authStore.refreshAccessToken()
            const newAccessToken = authStore.access_token
            processQueue(null, newAccessToken)
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
            return $http(originalRequest)
          } catch (err) {
            processQueue(err)
            return Promise.reject(err)
          } finally {
            isRefreshing = false
          }
        }
      }

      return Promise.reject(error)
    }
    $http.interceptors.response.use(handleResponse, handleResponseError)
    $http.interceptors.request.use(handleRequest, handleRequestError)
  },
}
