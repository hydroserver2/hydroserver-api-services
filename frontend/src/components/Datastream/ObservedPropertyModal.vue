<template>
  <v-card>
    <v-card-title>
      <span class="headline"
        >{{ isEdit ? 'Edit' : 'Add' }} Observed Property</span
      >
    </v-card-title>
    <v-card-text>
      <v-container>
        <v-form ref="myForm" v-model="valid" validate-on="blur">
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="observedProperty.name"
                label="Name"
                :rules="rules.requiredName"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="observedProperty.definition"
                label="Definition"
                :rules="rules.description"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="observedProperty.description"
                label="Description"
                :rules="rules.description"
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="observedProperty.variable_type"
                label="Variable Type"
                :rules="rules.requiredName"
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="observedProperty.variable_code"
                label="Variable Code"
                :rules="rules.requiredCode"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn-cancel @click="$emit('close')">Cancel</v-btn-cancel>
            <v-btn type="submit" @submit.prevent="uploadObservedProperty">{{
              isEdit ? 'Update' : 'Save'
            }}</v-btn>
          </v-card-actions>
        </v-form>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ObservedProperty } from '@/types'
import { useObservedPropertyStore } from '@/store/observedProperties'
import { VForm } from 'vuetify/components'
import { rules } from '@/utils/rules'

const opStore = useObservedPropertyStore()
const props = defineProps({ id: String })
const isEdit = computed(() => props.id != null)
const emit = defineEmits(['uploaded', 'close'])
const valid = ref(false)
const myForm = ref<VForm>()

const observedProperty = reactive<ObservedProperty>({
  id: '',
  name: '',
  definition: '',
  description: '',
  variable_type: '',
  variable_code: '',
})

async function uploadObservedProperty() {
  await myForm.value?.validate()
  if (!valid.value) return
  if (isEdit.value) await opStore.updateObservedProperty(observedProperty)
  else {
    const newOP = await opStore.createObservedProperty(observedProperty)
    emit('uploaded', String(newOP.id))
  }
  emit('close')
}

onMounted(async () => {
  await opStore.fetchObservedProperties()
  if (props.id) Object.assign(observedProperty, await opStore.getById(props.id))
})
</script>
