import { AxiosInstance } from 'axios'
import { ComponentInternalInstance, getCurrentInstance } from 'vue'

let app: ComponentInternalInstance | null = null

export function useApiClient() {
  if (!app) {
    app = getCurrentInstance()
  }
  const $http = app?.appContext.config.globalProperties.$http
  return $http as AxiosInstance
}
