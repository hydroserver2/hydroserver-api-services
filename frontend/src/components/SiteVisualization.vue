<template>
  <v-row class="pt-4 pb-4" align="center" justify="center">
    <v-col cols="10" lg="8">
      <v-card class="elevation-5">
        <h5 class="text-h5 pt-2 text-center">
          Datastream for {{ thing.name }}
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

const datastreamId = useRoute().params.datastreamId.toString()
const thingId = useRoute().params.id.toString()

const { thing } = useThing(thingId)
const { datastream, observations } = useDatastream(thingId, datastreamId)

let chart = ref<null | HTMLDivElement>(null)

watchEffect(drawD3Chart)

// Format the data
const data = observations.value.map((observation) => ({
  date: new Date(observation.result_time),
  value: Number(observation.result),
}))
data.sort((a, b) => a.date.getTime() - b.date.getTime())

function drawD3Chart() {
  if (!chart.value) return
  chart.value.innerHTML = ''

  const svg = drawChart(data, datastream.value.unit_name)
  if (svg) chart.value.appendChild(svg)
}
</script>
