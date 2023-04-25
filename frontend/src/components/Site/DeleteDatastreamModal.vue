<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        <span class="text-h5">Confirm Deletion</span>
      </v-card-title>
      <v-card-text>
        Are you sure you want to delete the following datastream? This is
        unrecoverable and will delete all associated observations
        <br />
        <br /><strong>ID:</strong> {{ datastreamId }} <br /><strong
          >Observed Property:</strong
        >
        {{ datastreamObservedProperty }} <br /><strong>Method/Sensor:</strong>
        {{ datastreamMethod }} <br /><strong>ProcessingLevel:</strong>
        {{ datastreamProcessingLevel }}
      </v-card-text>
      <v-card-actions>
        <v-btn color="red darken-1" text @click="$emit('close')">Cancel</v-btn>
        <v-btn color="green darken-1" text @click="deleteDatastream"
          >Confirm</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import axios from '@/plugins/axios.config'
import { ref, watch } from 'vue'
import { useDataStore } from '@/store/data'

export default {
  props: {
    thingId: String,
    datastreamId: String,
    datastreamObservedProperty: String,
    datastreamMethod: String,
    datastreamProcessingLevel: String,
    showDialog: Boolean,
  },
  setup(props, { emit }) {
    const dataStore = useDataStore()
    const dialog = ref(props.showDialog)

    watch(
      () => props.showDialog,
      (newValue) => {
        dialog.value = newValue
      }
    )

    async function removeThingFromLocalStorage() {
      const cachedThingName = `thing_${props.thingId}`
      delete dataStore[cachedThingName]
      localStorage.removeItem(cachedThingName)
    }

    async function deleteDatastream() {
      try {
        await axios.delete(`/datastreams/${props.datastreamId}`)
        await removeThingFromLocalStorage()
        emit('close')
        emit('deleted')
      } catch (error) {
        console.error('Error deleting datastream:', error)
      }
    }

    return { dialog, deleteDatastream }
  },
}
</script>
