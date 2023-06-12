<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ isEdit ? 'Edit' : 'Add' }} Unit</span>
    </v-card-title>
    <v-card-text>
      <v-container v-if="unit">
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="unit.name"
              label="Name"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="unit.symbol"
              label="Symbol"
              outlined
              required
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="unit.definition"
              label="Definition"
              outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="unit.unit_type"
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
import { computed, onMounted, reactive } from 'vue'
import { useUnitStore } from '@/store/unit'
import { Unit } from '@/types'

const unitStore = useUnitStore()
const props = defineProps({ id: String })
const isEdit = computed(() => props.id != null)
const emit = defineEmits(['uploaded', 'close'])

const unit = reactive<Unit>({
  id: '',
  person_id: '',
  name: '',
  symbol: '',
  definition: '',
  unit_type: '',
})

async function uploadUnit() {
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
