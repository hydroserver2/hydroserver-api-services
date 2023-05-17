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
              v-model="processingLevel.processing_level_code"
              label="Processing Level Code"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="processingLevel.definition"
              label="Definition"
              outlined
              required
            ></v-textarea>
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="processingLevel.explanation"
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
import { computed, onMounted, reactive } from 'vue'
import { ProcessingLevel } from '@/types'
import { useProcessingLevelStore } from '@/store/processingLevels'

const plStore = useProcessingLevelStore()
const props = defineProps({ plId: String })
const isEdit = computed(() => props.plId != null)

const processingLevel = reactive<ProcessingLevel>({
  id: '',
  person_id: '',
  processing_level_code: '',
  definition: '',
  explanation: '',
})

const emit = defineEmits(['uploaded', 'close'])

async function uploadProcessingLevel() {
  if (isEdit.value) {
    await plStore.updateProcessingLevel(processingLevel)
    emit('uploaded', String(processingLevel.id))
  } else {
    const newPl = await plStore.createProcessingLevel(processingLevel)
    emit('uploaded', String(newPl.id))
  }
  emit('close')
}

async function populateForm(id: string | undefined) {
  if (id) {
    const newPl = plStore.getProcessingLevelById(id)
    for (const key in newPl) {
      processingLevel[key] = newPl[key]
    }
  }
}

onMounted(async () => {
  await plStore.fetchProcessingLevels()
  await populateForm(props.plId)
})
</script>
