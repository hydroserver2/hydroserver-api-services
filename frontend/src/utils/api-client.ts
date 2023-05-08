import { AxiosInstance } from 'axios'
import { getCurrentInstance } from 'vue'

export function useApiClient() {
  const app = getCurrentInstance()
  const $http = app?.appContext.config.globalProperties.$http
  return $http as AxiosInstance
}
