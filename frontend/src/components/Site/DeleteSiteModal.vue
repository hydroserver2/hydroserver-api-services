<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        <span class="text-h5">Confirm Deletion</span>
      </v-card-title>
      <v-card-text>
        Please type the site name (<strong>{{ siteName }}</strong
        >) to confirm deletion:
        <v-form>
          <v-text-field
            v-model="deleteInput"
            label="Site name"
            solo
            @keydown.enter.prevent="deleteSite"
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="red darken-1" text @click="close">Cancel</v-btn>
        <v-btn color="green darken-1" text @click="deleteSite">Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from '@/plugins/axios.config'
import { useDataStore } from '@/store/data'
import router from '@/router/router'

const props = defineProps({
  siteId: String,
  siteName: String,
  showDialog: Boolean,
})
const emit = defineEmits(['deleted', 'close'])

const dataStore = useDataStore()
const dialog = ref(props.showDialog)
const deleteInput = ref('')

watch(
  () => props.showDialog,
  (newValue) => {
    dialog.value = newValue
  }
)

async function removeThingsFromLocalStorage() {
  localStorage.removeItem('things')
  dataStore.things = []
  const cachedThingName = `thing_${props.siteId}`
  delete dataStore[cachedThingName]
  localStorage.removeItem(cachedThingName)
}

async function deleteSite() {
  if (deleteInput.value !== props.siteName) {
    console.error('Site name does not match.')
    return
  }

  try {
    await axios.delete(`/things/${props.siteId}`)
    await removeThingsFromLocalStorage()
    close()
    emit('deleted')

    await dataStore.fetchOrGetFromCache('things', '/things')
    await router.push('/sites')
  } catch (error) {
    console.error('Error deleting site:', error)
  }
}

function close() {
  deleteInput.value = ''
  emit('close')
}
</script>
