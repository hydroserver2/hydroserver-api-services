import { useDatastreamStore } from '@/store/datastreams'
import { onMounted, computed, ref, Ref, watch } from 'vue'
import { useThing } from './useThing'
import { Datastream } from '@/types'
import Notification from '@/store/notifications'

export function useDatastreams(thingId: string) {
  const { is_owner } = useThing(thingId)
  const datastreamStore = useDatastreamStore()
  const selectedDatastream: Ref<Datastream | null> = ref(null)
  const isDeleteModalOpen = ref(false)
  const deleteDatastreamInput = ref('')

  const visibleDatastreams = computed(() => {
    if (!datastreamStore.datastreams[thingId]) return []

    return datastreamStore.datastreams[thingId]
      .filter((datastream) => datastream.is_visible || is_owner.value)
      .map((datastream) => ({
        ...datastream,
        chartOpen: false, // Adding a dialog boolean to each datastream so we can open a modal for each
      }))
  })

  async function toggleVisibility(datastream: Datastream) {
    datastream.is_visible = !datastream.is_visible
    await datastreamStore.setVisibility(datastream.id, datastream.is_visible)
  }

  function openDeleteModal(datastream: Datastream) {
    selectedDatastream.value = datastream
    isDeleteModalOpen.value = true
  }

  function closeDeleteModal() {
    selectedDatastream.value = null
    // isDeleteModalOpen.value = false
    deleteDatastreamInput.value = ''
  }

  watch(isDeleteModalOpen, (newValue) => {
    if (newValue === false) {
      closeDeleteModal()
    }
  })

  async function deleteDatastream() {
    if (deleteDatastreamInput.value !== 'Delete') {
      Notification.toast({
        message: 'inputs do not match',
        type: 'error',
      })
      return
    }
    isDeleteModalOpen.value = false
    if (selectedDatastream.value) {
      await datastreamStore.deleteDatastream(
        selectedDatastream.value.id,
        thingId
      )
    }
    deleteDatastreamInput.value = ''
  }

  onMounted(async () => {
    await datastreamStore.fetchDatastreamsByThingId(thingId)
  })

  return {
    visibleDatastreams,
    toggleVisibility,
    selectedDatastream,
    openDeleteModal,
    deleteDatastream,
    isDeleteModalOpen,
    deleteDatastreamInput,
  }
}
