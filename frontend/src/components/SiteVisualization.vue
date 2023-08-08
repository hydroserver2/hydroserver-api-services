<template>
  <v-row class="pt-4 pb-4" align="center" justify="center">
    <v-col cols="10" lg="8">
      <v-card class="elevation-5">
        <h5 class="text-h5 pt-2 text-center">
          Datastream for {{ thing?.name }}
        </h5>
        <div ref="chart"></div>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { useDatastream } from '@/composables/useDatastream'
import { useThing } from '@/composables/useThing'
import { drawChart } from '@/composables/chart'
import { onMounted } from 'vue'
import { useUnitStore } from '@/store/unit'

const unitStore = useUnitStore()

const datastreamId = useRoute().params.datastreamId.toString()
const thingId = useRoute().params.id.toString()

const { thing } = useThing(thingId)
const { datastream, observations } = useDatastream(thingId, datastreamId)

let chart = ref<null | HTMLDivElement>(null)

const data = observations.value.map((observation) => ({
  date: new Date(observation.result_time),
  value: Number(observation.result),
}))

watchEffect(drawD3Chart)

function drawD3Chart() {
  if (!chart.value) return
  chart.value.innerHTML = ''

  const unitSymbol = `(${
    unitStore.getUnitById(datastream.value.unit_id).symbol
  })`

  const yAxisLabel = datastream.value
    ? `${datastream.value.observed_property_name} ${unitSymbol} `
    : ''

  const svg = drawChart(data, yAxisLabel)
  if (svg) chart.value.appendChild(svg)
}

onMounted(async () => {
  await unitStore.fetchUnits()
})
</script>
