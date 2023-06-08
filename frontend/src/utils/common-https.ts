import axios from 'axios'
const baseUrl = import.meta.env.VITE_APP_PROXY_BASE_URL
const mode = import.meta.env.MODE

const apiClient = axios.create({
  baseURL: `${mode === 'development' ? 'http://127.0.0.1:8000' : baseUrl}/api/`,
  headers: {
    'Content-type': 'application/json',
    // 'Access-Control-Allow-Origin': '*',
  },
  validateStatus: (status) => status >= 200 && status < 300,
})

export default apiClient
