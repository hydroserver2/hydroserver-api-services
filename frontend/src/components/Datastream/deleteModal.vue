<template>
  <v-card>
    <v-card-title>
      <span class="text-h5">Confirm {{ itemName }} deletion</span>
    </v-card-title>
    <v-card-text>
      <div v-if="datastreamsForItem && datastreamsForItem.length > 0">
        This {{ itemName }} cannot be deleted because it's being referenced by
        some of your datastreams. Before this {{ itemName }} can be deleted, all
        related datastreams need to be removed or reassigned to another
        {{ itemName }}. The following datastreams are currently linked to this
        {{ itemName }}:
        <br />
        <div v-for="datastream in datastreamsForItem" :key="datastream.id">
          <br />
          DatastreamID: {{ (datastream as Datastream).id }} <br />
          Observed Property:
          {{ (datastream as Datastream).observed_property_name }}<br />
          Unit:
          {{ (datastream as Datastream).unit_name }}<br />
          Processing Level:
          {{ (datastream as Datastream).processing_level_name }}
          <br />
        </div>
      </div>
      <div v-else>
        This {{ itemName }} isn't being used by any datastreams and is safe to
        delete
      </div>
      <br />
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn-cancel @click="emit('close')">Cancel</v-btn-cancel>
      <v-btn
        v-if="!datastreamsForItem || datastreamsForItem.length <= 0"
        color="delete"
        @click="emit('delete')"
        >Delete</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { Datastream } from '@/types'
import { computed, onMounted } from 'vue'
import { useDatastreamStore } from '@/store/datastreams'

const datastreamStore = useDatastreamStore()
const emit = defineEmits(['delete', 'close'])
const props = defineProps({
  itemName: String,
  itemID: [String, Number],
  parameterName: String,
})

const datastreamsForItem = computed(() => {
  if (props.itemID && props.parameterName) {
    return datastreamStore.getDatastreamsByParameter(
      props.parameterName as keyof Datastream,
      props.itemID
    )
  }
})

onMounted(async () => await datastreamStore.fetchDatastreams())
</script>
