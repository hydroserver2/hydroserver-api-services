import { ref, onMounted, computed, watch, reactive } from 'vue'
import { VForm } from 'vuetify/components'
import { useSensorStore } from '@/store/sensors'
import { useUnitStore } from '@/store/unit'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { useProcessingLevelStore } from '@/store/processingLevels'
import { Sensor, Unit, ObservedProperty, ProcessingLevel } from '@/types'

function useMetadata(
  entityStore: any,
  createEntity: () => any,
  fetchEntities: string,
  deleteEntity: string,
  getEntityByID: string,
  id: string | null = null
) {
  const isCreateEditModalOpen = ref(false)
  const isDeleteModalOpen = ref(false)
  const isEdit = computed(() => id != null)
  const valid = ref(false)
  const myForm = ref<VForm>()

  // selectedId is watched so that when it changes,
  // the form is populated with the data from selectedEntity
  const selectedId = ref(id)
  const isEntitySelected = ref(false) // TODO: Can probably do without this
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

  watch(selectedId, async () => {
    if (!selectedId.value) return
    populateForm(selectedId.value)
    await myForm.value?.validate()
  })

  function populateForm(id: string) {
    Object.assign(selectedEntity.value, entityStore[getEntityByID](id))
  }

  onMounted(async () => {
    await entityStore[fetchEntities]()
    if (id) populateForm(id)
  })

  return {
    isEntitySelected,
    selectedId,
    selectedEntity,
    isCreateEditModalOpen,
    isDeleteModalOpen,
    isEdit,
    valid,
    myForm,
    deleteSelectedEntity,
    openDialog,
    openDeleteDialog,
  }
}

export function useSensors(id: string | null = null) {
  return useMetadata(
    useSensorStore(),
    () => new Sensor(),
    'fetchSensors',
    'deleteSensor',
    'getSensorById',
    id
  )
}

export function useUnits(id: string | null = null) {
  return useMetadata(
    useUnitStore(),
    () => new Unit(),
    'fetchUnits',
    'deleteUnit',
    'getUnitById',
    id
  )
}

export function useProcessingLevels(id: string | null = null) {
  const metadataFuncs = useMetadata(
    useProcessingLevelStore(),
    () => new ProcessingLevel(),
    'fetchProcessingLevels',
    'deleteProcessingLevel',
    'getProcessingLevelById',
    id
  )

  const plStore = useProcessingLevelStore()

  const formattedProcessingLevels = computed(() => {
    return plStore.unownedProcessingLevels.map((pl) => ({
      id: pl.id,
      title: `${pl.processing_level_code} : ${pl.definition}`,
    }))
  })

  return {
    ...metadataFuncs,
    formattedProcessingLevels,
  }
}

export function useObservedProperties(id: string | null = null) {
  return useMetadata(
    useObservedPropertyStore(),
    () => new ObservedProperty(),
    'fetchObservedProperties',
    'deleteObservedProperty',
    'getObservedPropertyById',
    id
  )
}
