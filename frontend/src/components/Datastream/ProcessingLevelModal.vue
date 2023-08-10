<template>
  <v-card>
    <v-card-title>
      <span class="headline"
        >{{ isEdit ? 'Edit' : 'Add' }} Processing Level</span
      >
    </v-card-title>
    <v-card-text>
      <v-container>
        <v-form
          @submit.prevent="uploadProcessingLevel"
          ref="myForm"
          v-model="valid"
          validate-on="blur"
        >
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="processingLevel.processing_level_code"
                label="Processing Level Code"
                :rules="rules.requiredCode"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="processingLevel.definition"
                label="Definition"
                :rules="rules.description"
              ></v-textarea>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="processingLevel.explanation"
                label="Explanation"
                :rules="rules.description"
              ></v-textarea>
            </v-col>
          </v-row>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn-cancel @click="$emit('close')">Cancel</v-btn-cancel>
            <v-btn type="submit">{{ isEdit ? 'Update' : 'Save' }}</v-btn>
          </v-card-actions>
        </v-form>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { VForm } from 'vuetify/components'
import { rules } from '@/utils/rules'
import { ProcessingLevel } from '@/types'
import { useProcessingLevelStore } from '@/store/processingLevels'

const plStore = useProcessingLevelStore()
const props = defineProps({ id: String })
const isEdit = computed(() => props.id != null)
const emit = defineEmits(['uploaded', 'close'])
const valid = ref(false)
const myForm = ref<VForm>()
const processingLevel = reactive<ProcessingLevel>(new ProcessingLevel())

async function uploadProcessingLevel() {
  await myForm.value?.validate()
  if (!valid.value) return
  if (isEdit.value) await plStore.updateProcessingLevel(processingLevel)
  else {
    const newPl = await plStore.createProcessingLevel(processingLevel)
    emit('uploaded', newPl.id)
  }
  emit('close')
}

onMounted(async () => {
  await plStore.fetchProcessingLevels()
  if (props.id)
    Object.assign(processingLevel, plStore.getProcessingLevelById(props.id))
})
</script>
