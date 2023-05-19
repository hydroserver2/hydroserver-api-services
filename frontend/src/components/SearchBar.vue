<template>
  <div>
    <v-text-field
      label="Filter by Organizations"
      prepend-inner-icon="mdi-magnify"
      clearable
      v-model="searchInput"
      @input="updateSearchFilter"
    ></v-text-field>

    <!-- <v-checkbox
      label="Regex"
      v-model="regex"
      @change="updateSearchFilter"
    ></v-checkbox>

    <v-checkbox
      label="Whole word"
      v-model="wholeWord"
      @change="updateSearchFilter"
    ></v-checkbox>

    <v-checkbox
      label="Case sensitive"
      v-model="caseSensitive"
      @change="updateSearchFilter"
    ></v-checkbox> -->
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  clearSearch: Boolean,
})

const emit = defineEmits(['filtered-items'])

const searchInput = ref('')
const regex = ref(false)
const wholeWord = ref(false)
const caseSensitive = ref(false)

const updateSearchFilter = () => {
  let filter = searchInput.value
  if (!filter) {
    emit('filtered-items', [])
    return
  }

  const flags = caseSensitive.value ? '' : 'i'
  let pattern = regex.value
    ? filter
    : filter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  if (wholeWord.value) pattern = `\\b${pattern}\\b`

  const regexFilter = new RegExp(pattern, flags)

  const filteredItems = props.items.filter((item) => regexFilter.test(item))
  emit('filtered-items', filteredItems)
}

const items = computed(() => props.items)

watch(items, () => {
  updateSearchFilter()
})

watchEffect(() => {
  if (props.clearSearch) {
    searchInput.value = ''
  }
})
</script>
