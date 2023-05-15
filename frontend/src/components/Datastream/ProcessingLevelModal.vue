<template>
  <v-card>
    <v-card-title>
      <span class="headline"
        >{{ isEdit ? 'Edit' : 'Add' }} Processing Level</span
      >
    </v-card-title>
    <v-card-text>
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="formData.processing_level_code"
              label="Processing Level Code"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="formData.definition"
              label="Definition"
              outlined
              required
            ></v-textarea>
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="formData.explanation"
              label="Explanation"
              outlined
            ></v-textarea>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="blue darken-1" text @click="$emit('close')">Cancel</v-btn>
      <v-btn color="blue darken-1" text @click="uploadProcessingLevel"
        >Submit</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/store/data'
import { useApiClient } from '@/utils/api-client'
const api = useApiClient()

const dataStore = useDataStore()
const formData = ref({
  processing_level_code: '',
  definition: '',
  explanation: '',
})

onMounted(() => {
  if (isEdit.value) {
    formData.value = {
      processing_level_code: props.processingLevel.processing_level_code || '',
      definition: props.processingLevel.definition || '',
      explanation: props.processingLevel.explanation || '',
    }
  }
})

const props = defineProps({
  processingLevel: { type: Object, default: null },
})

const isEdit = computed(() => {
  return props.processingLevel != null
})

const emit = defineEmits(['uploaded', 'close'])

async function uploadProcessingLevel() {
  try {
    if (isEdit.value) {
      await api.patch(
        `/processing-levels/${props.processingLevel.id}`,
        formData.value
      )
      localStorage.removeItem(`processingLevels`)
      dataStore.processingLevels = []
      emit('uploaded', String(props.processingLevel.id))
    } else {
      const response = await api.post('/processing-levels', formData.value)
      const newProcessingLevel = response.data
      dataStore.addProcessingLevel(newProcessingLevel)
      emit('uploaded', newProcessingLevel.id)
    }
    emit('close')
  } catch (error) {
    console.log('Error Registering Processing Level: ', error)
  }
}
</script>
