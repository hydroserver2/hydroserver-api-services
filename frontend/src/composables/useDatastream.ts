import { useDatastreamStore } from '@/store/datastreams'
import { onMounted, computed, ref, Ref } from 'vue'
import { Datastream } from '@/types'

export function useDatastream(thingId: string, id: string) {
  const dsStore = useDatastreamStore()

  const datastream = computed(
    () =>
      dsStore.getDatastreamForThingById(thingId, id) as unknown as Datastream
  )

  const observations = computed(() => {
    if (!datastream.value) return []
    return datastream.value.observations
  })

  //   async function toggleVisibility(datastream: Datastream) {
  //     datastream.is_visible = !datastream.is_visible
  //     await dsStore.setVisibility(datastream.id, datastream.is_visible)
  //   }

  onMounted(async () => {
    await dsStore.fetchDatastreamsByThingId(thingId)
  })

  return {
    // toggleVisibility,
    datastream,
    observations,
  }
}
