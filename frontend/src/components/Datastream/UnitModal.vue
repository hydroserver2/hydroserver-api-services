<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ isEdit ? 'Edit' : 'Add' }} Unit</span>
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
              v-model="formData.symbol"
              label="Symbol"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="formData.definition"
              label="Definition"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="formData.unit_type"
              label="Unit Type"
              outlined
              required
            ></v-text-field>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="blue darken-1" text @click="$emit('close')">Cancel</v-btn>
      <v-btn color="blue darken-1" text @click="uploadUnit">Submit</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from '@/plugins/axios.config'
import { useDataStore } from '@/store/data'

const emit = defineEmits(['uploaded', 'close'])

const props = defineProps({
  unit: { type: Object, default: null },
})

const isEdit = computed(() => {
  return props.unit != null
})

const dataStore = useDataStore()
const formData = ref({
  name: '',
  symbol: '',
  definition: '',
  unit_type: '',
})

onMounted(() => {
  if (isEdit.value) {
    formData.value = {
      name: props.unit.name || '',
      symbol: props.unit.symbol || '',
      definition: props.unit.definition || '',
      unit_type: props.unit.unit_type || '',
    }
  }
})

async function uploadUnit() {
  try {
    if (isEdit.value) {
      await axios.patch(`/units/${props.unit.id}`, formData.value)
      localStorage.removeItem(`units`)
      dataStore.units = []
      emit('uploaded', String(props.unit.id))
    } else {
      const response = await axios.post('/units', formData.value)
      const newUnit = response.data
      dataStore.addUnit(newUnit)
      emit('uploaded', newUnit.id)
    }
    emit('close')
  } catch (error) {
    console.log('Error Registering Unit: ', error)
  }
}
</script>
