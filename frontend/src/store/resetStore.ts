import { getActivePinia, Pinia, Store } from 'pinia'

interface ExtendedPinia extends Pinia {
  _s: Map<string, Store>
}

export function useResetStore() {
  const pinia = getActivePinia() as ExtendedPinia

  if (!pinia) {
    throw new Error('There is no active Pinia instance')
  }

  const resetStores: Record<string, () => void> = {}

  pinia._s.forEach((store, name) => {
    resetStores[name] = () => store.$reset()
  })

  resetStores.all = () => pinia._s.forEach((store) => store.$reset())

  return resetStores
}
