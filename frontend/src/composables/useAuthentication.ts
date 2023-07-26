import { useAuthStore } from '@/store/authentication'
import { computed } from 'vue'

export function useAuthentication() {
  const authStore = useAuthStore()

  const isAuthenticated = computed(() => !!authStore.access_token)

  return { isAuthenticated }
}
