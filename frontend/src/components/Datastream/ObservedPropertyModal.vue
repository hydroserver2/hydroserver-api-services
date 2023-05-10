<template>
  <v-card>
    <v-card-title>
      <span class="headline"
        >{{ isEdit ? 'Edit' : 'Add' }} Observed Property</span
      >
    </v-card-title>
    <v-card-text>
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="formData.name"
              label="Name"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="formData.definition"
              label="Definition"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="formData.description"
              label="Description"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="formData.variable_type"
              label="Variable Type"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="formData.variable_code"
              label="Variable Code"
              outlined
            ></v-text-field>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="blue darken-1" text @click="$emit('close')">Cancel</v-btn>
      <v-btn color="blue darken-1" text @click="uploadObservedProperty">{{
        isEdit ? 'Update' : 'Save'
      }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from '@/plugins/axios.config'
import { useDataStore } from '@/store/data'

const props = defineProps({
  observedProperty: { type: Object, default: null },
})

const isEdit = computed(() => {
  return props.observedProperty != null
})

const dataStore = useDataStore()
const formData = ref({
  name: '',
  definition: '',
  description: '',
  variable_type: '',
  variable_code: '',
})
onMounted(() => {
  console.log('Mounted')
  console.log('props.observedProperty', props.observedProperty)
  if (isEdit.value) {
    formData.value = {
      name: props.observedProperty.name || '',
      definition: props.observedProperty.definition || '',
      description: props.observedProperty.description || '',
      variable_type: props.observedProperty.variable_type || '',
      variable_code: props.observedProperty.variable_code || '',
    }
  }
})

const emit = defineEmits(['uploaded', 'close'])

async function uploadObservedProperty() {
  try {
    if (isEdit.value) {
      await axios.patch(
        `/observed-properties/${props.observedProperty.id}`,
        formData.value
      )
      localStorage.removeItem(`observedProperties`)
      dataStore.observedProperties = []
      emit('uploaded', String(props.observedProperty.id))
    } else {
      const response = await axios.post('/observed-properties', formData.value)
      const newObservedProperty = response.data
      dataStore.addObservedProperty(newObservedProperty)
      emit('uploaded', String(newObservedProperty.id))
    }
    emit('close')
  } catch (error) {
    console.log('Error Registering Observed Property: ', error)
  }
}
</script>
