import axios from 'axios'
import router from '@/router/router'
import { useAuthStore } from '@/store/authentication'

axios.defaults.baseURL = `${
  import.meta.env.MODE === 'development'
    ? 'http://127.0.0.1:8000'
    : PROXY_BASE_URL // TODO: set env variable for this
}/api/`

// TODO: move these configs to a store with an init method
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error)
    else prom.resolve(token)
  })
  failedQueue = []
}

// Axios interceptor for handling JWT tokens
axios.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.access_token)
      config.headers.Authorization = `Bearer ${authStore.access_token}`

    if (authStore.refresh_token)
      config.headers.Refresh_Authorization = `Bearer ${authStore.refresh_token}`
    return config
  },
  (error) => Promise.reject(error)
)

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    if (
      error.response.status === 401 &&
      originalRequest.url === '/token/refresh'
    ) {
      console.log('Refresh Token has failed. Redirecting to login page...')
      await authStore.logout()
      await router.push('/login')
      return Promise.reject(error)
    }

    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return axios(originalRequest)
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
        return axios(originalRequest)
      } catch (err) {
        processQueue(err)
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default axios
