<template>
  <v-dialog v-model="dialog" max-width="600px">
    <template v-slot:activator="{ on, attrs }">
      <v-btn color="primary" dark v-bind="attrs" @click="dialog = true"
        >Add Processing Level</v-btn
      >
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Add Processing Level</span>
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
        <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="createProcessingLevel"
          >Submit</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import axios from '@/plugins/axios.config'
import { ref } from 'vue'
import { useDataStore } from '@/store/data'

const dataStore = useDataStore()
const dialog = ref(false)
const formData = ref({
  processing_level_code: '',
  definition: '',
  explanation: '',
})

const emit = defineEmits(['processingLevelCreated'])

async function createProcessingLevel() {
  try {
    const response = await axios.post('/processing-levels', formData.value)
    const newProcessingLevel = response.data
    dataStore.addProcessingLevel(newProcessingLevel)
    dialog.value = false
    emit('processingLevelCreated', newProcessingLevel.id)
  } catch (error) {
    console.log('Error Registering Processing Level: ', error)
  }
}
</script>
