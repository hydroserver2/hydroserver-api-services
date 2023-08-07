import { useThingStore } from '@/store/things'
import { Thing } from '@/types'
import { onMounted } from 'vue'
import { computed, ref } from 'vue'
import { useAuthentication } from './useAuthentication'
import router from '@/router/router'

export function useThing(thingId: string) {
  const { isAuthenticated } = useAuthentication()
  const thingStore = useThingStore()

  const deleteInput = ref('')
  const isRegisterModalOpen = ref(false)
  const isDeleteModalOpen = ref(false)
  const isAccessControlModalOpen = ref(false)

  const is_owner = computed(() => {
    if (isAuthenticated && thingStore.things[thingId]) {
      return thingStore.things[thingId].owns_thing
    }
    return false
  })

  const isPrimaryOwner = computed(() => {
    if (isAuthenticated && thingStore.things[thingId]) {
      return thingStore.things[thingId].is_primary_owner
    }
    return false
  })

  function switchToAccessControlModal() {
    isDeleteModalOpen.value = false
    isAccessControlModalOpen.value = true
  }

  // const { things } = storeToRefs(thingStore)
  const thing = computed(() => thingStore.things[thingId] as unknown as Thing)

  //TODO: Find a better way to get GoogleMaps to reload on thing change
  const stringThing = computed(
    () => thingStore.things[thingId] as unknown as string
  )

  const mapOptions = computed(() => {
    if (thingStore.things[thingId])
      return {
        center: {
          lat: thingStore.things[thingId].latitude,
          lng: thingStore.things[thingId].longitude,
        },
        zoom: 16,
        mapTypeId: 'satellite',
      }
  })

  const thingProperties = computed(() => {
    if (!thing.value) return []
    const {
      id,
      sampling_feature_code,
      latitude,
      longitude,
      elevation,
      description,
      sampling_feature_type,
      site_type,
      state,
      county,
      is_private,
      owners,
    } = thing.value

    return [
      { icon: 'fas fa-id-badge', label: 'ID', value: id },
      {
        icon: 'fas fa-barcode',
        label: 'Site Code',
        value: sampling_feature_code,
      },
      { icon: 'fas fa-map', label: 'Latitude', value: latitude },
      { icon: 'fas fa-map', label: 'Longitude', value: longitude },
      { icon: 'fas fa-mountain', label: 'Elevation', value: elevation },
      { icon: 'fas fa-file-alt', label: 'Description', value: description },
      {
        icon: 'fas fa-map-marker-alt',
        label: 'Sampling Feature Type',
        value: sampling_feature_type,
      },
      { icon: 'fas fa-map-pin', label: 'Site Type', value: site_type },
      { icon: 'fas fa-flag-usa', label: 'State', value: state },
      { icon: 'fas fa-flag-usa', label: 'County', value: county },
      {
        icon: is_private ? 'fas fa-lock' : 'fas fa-globe',
        label: 'Privacy',
        value: is_private ? 'Private' : 'Public',
      },
      {
        icon: 'fas fa-user',
        label: 'Site Owners',
        value: owners
          .map(
            (owner) =>
              `${owner.firstname} ${owner.lastname}: ${owner.organization}`
          )
          .join(', '),
      },
    ]
  })

  function updateFollow() {
    if (thingStore.things[thingId]) {
      thingStore.updateThingFollowership(thingStore.things[thingId])
    }
  }

  async function deleteThing() {
    if (!thing.value) {
      console.error('Site could not be found.')
      return
    }
    if (deleteInput.value !== thing.value.name) {
      console.error('Site name does not match.')
      return
    }
    await thingStore.deleteThing(thingId)
    await router.push('/sites')
  }

  const newOwnerEmail = ref('')
  const newPrimaryOwnerEmail = ref('')
  const showPrimaryOwnerConfirmation = ref(false)

  async function addSecondaryOwner() {
    if (newOwnerEmail.value) {
      await thingStore.addSecondaryOwner(thingId, newOwnerEmail.value)
      newOwnerEmail.value = ''
    }
  }

  async function transferPrimaryOwnership() {
    if (newPrimaryOwnerEmail.value) {
      await thingStore.transferPrimaryOwnership(
        thingId,
        newPrimaryOwnerEmail.value
      )
      newPrimaryOwnerEmail.value = ''
      showPrimaryOwnerConfirmation.value = false
    }
  }

  async function removeOwner(email: string) {
    if (email) await thingStore.removeOwner(thingId, email)
  }

  async function toggleSitePrivacy() {
    await thingStore.updateThingPrivacy(thingId, thing.value.is_private)
  }

  onMounted(async () => {
    await thingStore.fetchThingById(thingId)
  })

  return {
    newOwnerEmail,
    newPrimaryOwnerEmail,
    addSecondaryOwner,
    showPrimaryOwnerConfirmation,
    transferPrimaryOwnership,
    removeOwner,
    toggleSitePrivacy,
    thing,
    mapOptions,
    updateFollow,
    is_owner,
    isPrimaryOwner,
    deleteInput,
    deleteThing,
    thingProperties,
    isRegisterModalOpen,
    isDeleteModalOpen,
    isAccessControlModalOpen,
    switchToAccessControlModal,
    stringThing,
  }
}
