import { useDatastreamStore } from '@/store/datastreams'
import { onMounted, computed, ref, Ref } from 'vue'
import { useThing } from './useThing'
import { Datastream } from '@/types'

export function useDatastreams(thingId: string) {
  const { is_owner } = useThing(thingId)
  const datastreamStore = useDatastreamStore()
  const selectedDatastream: Ref<Datastream | null> = ref(null)
  const isDeleteModalOpen = ref(false)

  const visibleDatastreams = computed(() => {
    if (!datastreamStore.datastreams[thingId]) return []
    return datastreamStore.datastreams[thingId].filter(
      (datastream) => datastream.is_visible || is_owner.value
    )
  })

  async function toggleVisibility(datastream: Datastream) {
    datastream.is_visible = !datastream.is_visible
    await datastreamStore.setVisibility(datastream.id, datastream.is_visible)
  }

  function openDeleteModal(datastream: Datastream) {
    selectedDatastream.value = datastream
    isDeleteModalOpen.value = true
  }

  async function deleteDatastream() {
    isDeleteModalOpen.value = false
    if (selectedDatastream.value) {
      await datastreamStore.deleteDatastream(
        selectedDatastream.value.id,
        thingId
      )
    }
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
  }
}
