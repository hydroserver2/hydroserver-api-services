<template>
  <div ref="chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watchEffect } from 'vue'
import * as d3 from 'd3'
import { PropType } from 'vue'
import { Observation } from '@/types'

const props = defineProps({
  observations: {
    type: Array as PropType<Observation[]>,
    required: true,
  },
})

const chart = ref<HTMLDivElement | null>(null)

onMounted(drawChart)

watchEffect(drawChart)

function drawChart() {
  if (chart.value) {
    chart.value.innerHTML = ''

    const margin = { top: 10, right: 0, bottom: 10, left: 0 },
      width = 250 - margin.left - margin.right,
      height = 120 - margin.top - margin.bottom

    const svg = d3
      .select(chart.value)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const data = props.observations.map((observation) => ({
      date:
        d3.timeParse('%Y-%m-%dT%H:%M:%S')(observation.result_time) ||
        new Date(),
      value: +observation.result, // Result is cast to number here.
    }))

    const x = d3
      .scaleTime()
      .domain(d3.extent(data, (d) => d.date) as [Date, Date])
      .range([0, width])

    svg.append('g').attr('transform', `translate(0,${height})`)
    // .call(d3.axisBottom(x))

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => +d.value) as number])
      .range([height, 0])

    // svg.append('g').call(d3.axisLeft(y))

    // Define the area
    let area = d3
      .area<{ date: Date | null; value: number }>()
      .x(function (d) {
        return x(d.date as Date)
      })
      .y0(height)
      .y1(function (d) {
        return y(d.value)
      })

    // Add the area
    svg
      .append('path')
      .datum(data)
      .attr('class', 'area')
      .attr('d', area)
      .style('fill', 'lightblue') //Color under the line

    svg
      .append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', 'steelblue') // Color the line
      .attr('stroke-width', 2.5)
      .attr(
        'd',
        d3
          .line<{ date: Date | null; value: number }>()
          .x((d) => x(d.date as Date))
          .y((d) => y(d.value))
      )

    svg
      .append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('height', height)
      .attr('width', width)
      .style('stroke', 'grey') // the color of the border
      .style('fill', 'none') // this means the inside of the rectangle is transparent
      .style('stroke-width', 2) // the width of the border
  }
}
</script>
