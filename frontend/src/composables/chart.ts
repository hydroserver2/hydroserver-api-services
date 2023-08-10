import * as d3 from 'd3'

type ChartData = {
  date: Date
  value: number
}

let previousDate: Date
let previousHour: number | null = null

const customTimeFormat = (date: Date) => {
  if (
    previousDate &&
    previousDate.getDate() === date.getDate() &&
    previousDate.getMonth() === date.getMonth() &&
    previousDate.getFullYear() === date.getFullYear()
  ) {
    if (previousHour !== null && previousHour === date.getHours()) {
      return d3.timeFormat('%I:%M%p')(date)
    } else {
      previousHour = date.getHours()
      return d3.timeFormat('%I%p')(date)
    }
  } else {
    previousDate = date
    previousHour = date.getHours()
    return d3.timeFormat('%B %d')(date)
  }
}

export function drawChart(
  data: ChartData[],
  yAxisLabel: string
): SVGSVGElement | null {
  if (!data || data.length === 0) {
    console.warn('Data array is empty, cannot draw chart')
    return null
  }

  data.sort((a, b) => a.date.getTime() - b.date.getTime())

  // Set dimensions and margins
  const margin = { top: 20, right: 20, bottom: 30, left: 30 }
  const width = 928
  const height = 500
  const labelWidth = 50

  // Create the horizontal and vertical scales
  let x = d3.scaleUtc().range([0, width - margin.right])
  const y = d3.scaleLinear().range([height - margin.bottom, margin.top])

  // Set the input range of the scales
  x.domain([data[0].date, data[data.length - 1].date])
  y.domain(d3.extent(data, (d) => d.value) as [number, number])

  const starterX = x
  // Create the horizontal axis generator, called at startup and when zooming.
  const xAxis = (g: any, x: any) =>
    g.call(
      d3
        .axisBottom(x)
        .ticks(width / 150)
        .tickSizeOuter(0)
        .tickFormat(customTimeFormat as any)
    )

  // The line generator, called at startup and when zooming.
  const line = (data: ChartData[], x: d3.ScaleTime<number, number>) =>
    d3
      .line<ChartData>()
      .x((d) => x(d.date))
      .y((d) => y(d.value))(data)

  // Create the zoom behavior.
  const zoom = d3
    .zoom()
    .scaleExtent([1, 32])
    .extent([
      [margin.left, 0],
      [width - margin.right, height],
    ])
    .translateExtent([
      [margin.left, -Infinity],
      [width - margin.right, Infinity],
    ])
    .on('zoom', zoomed)

  // Create SVG canvas
  const svg = d3
    .create('svg')
    .attr('viewBox', [
      0,
      0,
      width + margin.right + margin.left + labelWidth,
      height + margin.top + margin.bottom,
    ])

  // Create the main group element to the svg and add margins
  const plot_g = svg
    .append('g')
    .classed('plot', true)
    .attr('transform', `translate(${margin.left + labelWidth}, ${margin.top})`)

  // Make it so multiple instances of this chart don't interfere with each other
  let clipIdCounter = 0
  const clip = `clip${clipIdCounter++}`

  plot_g
    .append('clipPath')
    .attr('id', clip)
    .append('rect')
    .attr('width', width - margin.right)
    .attr('height', height)

  // Append the horizontal axis
  const gx = plot_g
    .append('g')
    .attr('transform', `translate(${0},${height - margin.bottom})`)
    .call(xAxis, x)

  // Append the vertical axis
  plot_g
    .append('g')
    .attr('transform', `translate(${0},${0})`)
    .call(d3.axisLeft(y))

  // Append a rectangle to the graph for mouseover events
  let background = plot_g
    .append('rect')
    .attr('width', width - margin.right)
    .attr('height', height - margin.bottom)
    .attr('fill', 'blue')
    .attr('fill-opacity', 0.0)

  // Create the Line
  const path = plot_g
    .append('path')
    .attr('clip-path', `url(#${clip})`)
    .attr('fill', 'none')
    .attr('stroke', '#4CAF50') // Material Green
    .attr('stroke-width', 2)
    .attr('d', line(data, x))

  // Append x-axis label
  plot_g
    .append('text')
    .attr('transform', `translate(${width / 2} ,${height + margin.top})`)
    .style('text-anchor', 'middle')
    .text('Date/Time')

  // Append y-axis label
  plot_g
    .append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', 0 - margin.left - labelWidth)
    .attr('x', 0 - height / 2)
    .attr('dy', '1em')
    .style('text-anchor', 'middle')
    .text(yAxisLabel)

  const mouse_g = plot_g
    .append('g')
    .classed('mouse', true)
    .style('display', 'none')
  mouse_g
    .append('rect')
    .attr('width', 2)
    .attr('x', -1)
    .attr('height', height)
    .attr('fill', 'lightgray')
  mouse_g
    .append('circle')
    .attr('clip-path', `url(#${clip})`)
    .attr('r', 3)
    .attr('stroke', 'steelblue')
  mouse_g.append('text')

  plot_g.on('mouseover', function (mouse) {
    mouse_g.style('display', 'block')
  })

  let highlightedDataIndex: any = null

  plot_g.on('mousemove', function (event) {
    // Get the current mouse x position in graph coordinates
    const [mouseX] = d3.pointer(event, this)

    // Convert the x position to a date
    const mouseDate = x.invert(mouseX)

    // Find the closest data point
    const bisect = d3.bisector((d: ChartData) => d.date).left
    const idx = bisect(data, mouseDate)
    highlightedDataIndex = idx

    const d0 = data[idx - 1]
    const d1 = data[idx]
    if (!d0 || !d1) return

    const d =
      mouseDate.getTime() - d0.date.getTime() >
      d1.date.getTime() - mouseDate.getTime()
        ? d1
        : d0

    // Set the position of the circle to the data point position
    mouse_g.select('circle').attr('cx', x(d.date)).attr('cy', y(d.value))

    // Set the position of the line to the x position
    mouse_g.select('rect').attr('transform', `translate(${mouseX}, 0)`)

    // Set the content and position of the text
    mouse_g
      .select('text')
      .text(`${d.value} - ${d3.timeFormat('%B %d, %Y %I:%M:%S %p')(d.date)}`)
      .attr('text-anchor', 'start')
      .attr('transform', `translate(0,0)`)
  })

  plot_g.on('mouseout', function (mouse) {
    mouse_g.style('display', 'none')
  })

  // When zooming, redraw the area and the x axis.
  function zoomed(event: any) {
    x = event.transform.rescaleX(starterX)
    path.attr('d', line(data, x))
    gx.call(xAxis, x)

    // If a data point is highlighted (i.e., the circle was moved before), update its position
    if (highlightedDataIndex !== null) {
      const d = data[highlightedDataIndex]
      mouse_g.select('circle').attr('cx', x(d.date)).attr('cy', y(d.value))
    }
  }

  // Initial zoom.
  svg
    .call(zoom as any)
    .transition()
    .duration(750)
    .call(zoom.transform as any, d3.zoomIdentity)

  return svg.node()
}
