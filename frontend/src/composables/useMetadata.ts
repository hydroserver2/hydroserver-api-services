import { ref, onMounted } from 'vue'
import { useSensorStore } from '@/store/sensors'
import { useUnitStore } from '@/store/unit'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { Sensor, Unit, ObservedProperty, ProcessingLevel } from '@/types'

function useMetadata(
  entityStore: any,
  createEntity: () => any,
  fetchEntities: string,
  deleteEntity: string
) {
  const isCreateEditModalOpen = ref(false)
  const isDeleteModalOpen = ref(false)
  const isEntitySelected = ref(false)
  const selectedEntity = ref(createEntity())

  function openDialog(
    myEntity?: Sensor | Unit | ObservedProperty | ProcessingLevel
  ) {
    isCreateEditModalOpen.value = true
    isEntitySelected.value = !!myEntity
    selectedEntity.value = myEntity ? myEntity : createEntity()
  }

  function openDeleteDialog(entity: any) {
    isDeleteModalOpen.value = true
    isEntitySelected.value = true
    selectedEntity.value = entity
  }

  async function deleteSelectedEntity() {
    isDeleteModalOpen.value = false
    await entityStore[deleteEntity](selectedEntity.value.id)
  }

  onMounted(async () => entityStore[fetchEntities]())

  return {
    isEntitySelected,
    selectedEntity,
    isCreateEditModalOpen,
    isDeleteModalOpen,
    deleteSelectedEntity,
    openDialog,
    openDeleteDialog,
  }
}

export function useSensors() {
  return useMetadata(
    useSensorStore(),
    () => new Sensor(),
    'fetchSensors',
    'deleteSensor'
  )
}

export function useUnits() {
  return useMetadata(
    useUnitStore(),
    () => new Unit(),
    'fetchUnits',
    'deleteUnit'
  )
}

export function useProcessingLevels() {
  return useMetadata(
    useProcessingLevelStore(),
    () => new ProcessingLevel(),
    'fetchProcessingLevels',
    'deleteProcessingLevel'
  )
}

export function useObservedProperties() {
  return useMetadata(
    useObservedPropertyStore(),
    () => new ObservedProperty(),
    'fetchObservedProperties',
    'deleteObservedProperty'
  )
}
