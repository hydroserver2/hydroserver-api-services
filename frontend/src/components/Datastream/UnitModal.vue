<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ isEdit ? 'Edit' : 'Add' }} Unit</span>
    </v-card-title>
    <v-card-text>
      <v-container v-if="unit">
        <v-form
          @submit.prevent="uploadUnit"
          ref="myForm"
          v-model="valid"
          validate-on="blur"
        >
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="unit.name"
                label="Name"
                :rules="rules.requiredName"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="unit.symbol"
                label="Symbol"
                :rules="rules.required"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="unit.definition"
                label="Definition"
                :rules="rules.description"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="unit.unit_type"
                label="Unit Type"
                :rules="rules.requiredName"
              ></v-text-field>
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
import { useUnitStore } from '@/store/unit'
import { Unit } from '@/types'

const unitStore = useUnitStore()
const props = defineProps({ id: String })
const isEdit = computed(() => props.id != null)
const emit = defineEmits(['uploaded', 'close'])
const valid = ref(false)
const myForm = ref<VForm>()

const unit = reactive<Unit>({
  id: '',
  person_id: '',
  name: '',
  symbol: '',
  definition: '',
  unit_type: '',
})

async function uploadUnit() {
  await myForm.value?.validate()
  if (!valid.value) return
  if (isEdit.value) await unitStore.updateUnit(unit)
  else {
    const newUnit = await unitStore.createUnit(unit)
    emit('uploaded', newUnit.id)
  }
  emit('close')
}

onMounted(async () => {
  await unitStore.fetchUnits()
  if (props.id) Object.assign(unit, await unitStore.getUnitById(props.id))
})
</script>
