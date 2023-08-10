<template>
  <div>
    <v-select :items="items" v-model="selectedItem" :label="label"></v-select>

    <v-dialog
      v-model="isDialogOpen"
      class="d-flex align-center justify-center"
      width="40rem"
      @update:modelValue="handleDialogClose"
    >
      <v-card>
        <v-card-title>Custom {{ label }}</v-card-title>
        <v-col>
          <v-text-field
            autofocus
            v-model="selectedItemCustom"
            :label="'Type in a custom ' + label.toLowerCase() + ' name'"
            @keydown.enter="selectCustom"
          ></v-text-field>
        </v-col>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelCustom">Cancel</v-btn>
          <v-btn @click="selectCustom">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps({
  items: Array,
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])
const isDialogOpen = ref(false)
const selectedItem = ref(props.modelValue)
const selectedItemCustom = ref('')
const previousSelectedItem = ref('')

watch(selectedItem, (newVal, oldVal) => {
  if (newVal === 'Enter custom name') {
    previousSelectedItem.value = oldVal
    isDialogOpen.value = true
  } else {
    if (props.modelValue !== newVal) emit('update:modelValue', newVal)
  }
})

const selectCustom = () => {
  selectedItem.value = selectedItemCustom.value
  isDialogOpen.value = false
}

const cancelCustom = () => {
  selectedItem.value = previousSelectedItem.value
  isDialogOpen.value = false
}

const handleDialogClose = (newValue: boolean) => {
  if (!newValue && selectedItem.value === 'Enter custom name') {
    selectedItem.value = previousSelectedItem.value
  }
}
</script>
