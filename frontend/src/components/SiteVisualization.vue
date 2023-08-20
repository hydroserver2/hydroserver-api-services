<template>
  <v-card class="elevation-5">
    <v-row>
      <v-col>
        <h5 class="text-h5 pt-2 text-center">
          Datastream for {{ thing?.name }}
        </h5>
      </v-col>
      <v-col cols="auto">
        <v-btn class="pt-2 pr-2" icon @click="$emit('close')">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <div ref="chart"></div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { useDatastream } from '@/composables/useDatastream'
import { useThing } from '@/composables/useThing'
import { drawChart } from '@/composables/chart'

const props = defineProps({
  thingId: {
    type: String,
    required: true,
  },
  datastreamId: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['close'])

const { thing } = useThing(props.thingId)
const { datastream, observations } = useDatastream(
  props.thingId,
  props.datastreamId
)

let chart = ref<null | HTMLDivElement>(null)

const data = observations.value.map((observation) => ({
  date: new Date(observation.result_time),
  value: Number(observation.result),
}))

watchEffect(drawD3Chart)

function drawD3Chart() {
  if (!chart.value) return
  chart.value.innerHTML = ''

  const unitSymbol = datastream.value.unit_symbol
    ? `(${datastream.value.unit_symbol})`
    : ''

  const yAxisLabel = datastream.value
    ? `${datastream.value.observed_property_name} ${unitSymbol} `
    : ''

  const svg = drawChart(data, yAxisLabel)
  if (svg) chart.value.appendChild(svg)
}
</script>
