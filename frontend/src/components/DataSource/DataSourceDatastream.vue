<template>
  <v-container>
    <v-row>
      <v-col class="v-col-xs-12 v-col-sm-6">
        <v-radio-group
          v-model="store.datastreamType"
          inline
        >
          <v-radio
            label="Column Index"
            value="index"
          ></v-radio>
          <v-radio
            label="Column Name"
            value="name"
          ></v-radio>
        </v-radio-group>
      </v-col>
      <v-col v-if="store.datastreamType === 'index'" class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="datastreamColumnIndex"
          v-model.number="store.datastreamColumn"
          label="Datastream Column"
          type="number"
          :rules="[
             (val) => val != null || 'Column index is required.',
             (val) => +val > 0 || 'Column index must be greater than zero.'
          ]"
        />
      </v-col>
      <v-col v-if="store.datastreamType === 'name'" class="v-col-xs-12 v-col-sm-6">
        <v-text-field
          ref="datastreamColumnName"
          v-model="store.datastreamColumn"
          label="Datastream Column"
          :rules="[
            (val) => val !== '' && val != null || 'Must enter datastream column name.'
          ]"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useDataSourceFormStore } from '@/store/datasource_form';

const store = useDataSourceFormStore()

const datastreamColumnIndex = ref()
const datastreamColumnName = ref()

async function validate() {
  let errors = []

  if (store.datastreamType === 'index') {
    errors.push(...(await datastreamColumnIndex.value.validate()))
  } else if (store.datastreamType === 'name') {
    errors.push(...(await datastreamColumnName.value.validate()))
  }

  return errors.length === 0
}

defineExpose({
  validate
})

</script>

<style scoped>

</style>