<template>
    <div class="flex flex-wrap justify-between px-8 py-4 mb-8">
        <div class="w-full mb-8 lg:w-1/2">
          <h3 class="mb-2 text-lg font-semibold">Active HTTP Server Requests</h3>
          <p class="mb-2 text-sm text-gray-600">Displays the number of active HTTP server requests over time, provides insights into server load and traffic patterns.</p>
          <div id="lineChart" ref="lineChartRef" class="h-80"></div>
        </div>
        <!-- <div id="lineChart" ref="lineChartRef" style="width: 600px; height: 400px'" class="mb-8"></div> -->
        <div v-for="(ref, index) in histogramChartRefs" :key="index" class="w-full mb-8 lg:w-1/2">
          <h3 class="mb-2 text-lg font-semibold">{{ chartTitles[index] }}</h3>
          <p class="mb-2 text-sm text-gray-600">{{ getExplanation(chartTitles[index]) }}</p>
          <div :id="`histogramChart-container-${index}`" :ref="ref" class="h-80"></div>
        </div>
        <div id="histogramChart-container-0" ref="histogramChartRef0" style="width: 600px; height: 400px;" class="mb-8"></div>
        <div id="histogramChart-container-1" ref="histogramChartRef1" style="width: 600px; height: 400px;" class="mb-8"></div>
        <div id="histogramChart-container-2" ref="histogramChartRef2" style="width: 600px; height: 400px;" class="mb-8"></div>
    </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import sdk from '../application-ui-sdk/src/index';

import api from '../api';

const { BaseChart } = sdk;

const lineChartRef = ref(null)
const histogramChartRef0 = ref(null)
const histogramChartRef1 = ref(null)
const histogramChartRef2 = ref(null)

const histogramCharts = ref([])
const histogramChartRefs = [histogramChartRef0, histogramChartRef1, histogramChartRef2]

let lineChart = null
let barChart = null
let histogramChart = null

const fetchMetrics = async () => {
    try {
        const payload = {
            keyword: ''
        }
        const response = await api.fetchTelemetryMetrics(payload)
        console.log(response, "<-- response");
        // if (response && response.length) {
        //     metricsData.value = response
        // } else {
        //     metricsData.value = [];
        // }
        return response
    } catch (error) {
        console.log(error);
        return []
    }
}

const chartTitles = computed(() => [
    'HTTP Request Duration',
    'HTTP Response Size',
    'HTTP Request Size'
])

const getExplanation = (title) => {
    if (title.includes('Duration')) {
        return 'Shows the distribution of request processing times. Data is grouped into time ranges (in milliseconds).';
    } else if (title.includes('Response Size')) {
        return 'Illustrates the distribution of response data volumes. Data is grouped into size ranges (in bytes).';
    } else if (title.includes('Request Size')) {
        return 'Displays the distribution of incoming data volumes. Data is grouped into size ranges (in bytes).';
    }
    return 'Data is grouped into ranges to show the overall distribution.';
};

// Function to process histogram data
function processHistogramData(dataPoints) {
    const buckets = dataPoints[0].histogram.explicitBounds
    return dataPoints.map(point => {
        const counts = point.histogram.bucketCounts.map(Number)
        return buckets.map((bound, index) => {
            const nextBound = buckets[index + 1] || Infinity
            return [bound, nextBound, counts[index]]
        })
    })
}

function createHistogramChart(container, title, xAxisName, seriesData) {
    // Limit to top 10 datasets with the highest total counts
    const topDatasets = seriesData
        .map((data, index) => ({
            data,
            totalCount: data.reduce((sum, item) => sum + item[2], 0),
            index
        }))
        .sort((a, b) => b.totalCount - a.totalCount)
        .slice(0, 10);

    // Group buckets into fewer categories
    const groupedData = topDatasets.map(dataset => {
        const groupedCounts = [0, 0, 0, 0, 0]; // 5 groups
        dataset.data.forEach(item => {
            const value = item[0];
            const count = item[2];
            if (value < 10) groupedCounts[0] += count;
            else if (value < 100) groupedCounts[1] += count;
            else if (value < 1000) groupedCounts[2] += count;
            else if (value < 10000) groupedCounts[3] += count;
            else groupedCounts[4] += count;
        });
        return groupedCounts;
    });

    const maxCount = Math.max(...groupedData.flat());
    const option = {
        container: container.id,
        tooltip: {
            trigger: 'item',
            formatter: function (params) {
                return `${params.seriesName}<br/>${params.name}: ${params.value}`;
            }
        },
        xAxis: {
            name: xAxisName,
            type: 'category',
            data: ['0-9', '10-99', '100-999', '1000-9999', '10000+'],
            axisLabel: {
                rotate: 45,
                interval: 0,
                fontSize: 10
            }
        },
        yAxis: {
            name: 'Frequency',
            type: 'value',
            max: maxCount * 1.1
        },
        series: groupedData.slice(0, 5).map((data, index) => ({
            name: `Dataset ${index + 1}`,
            type: 'bar',
            data: data,
            stack: 'total',
            barWidth: '50%',
        })),
        grid: {
            left: '10%',
            right: '10%',
            bottom: '20%',
            top: '10%',
            containLabel: false
        },
        legend: {
            type: 'scroll',
            orient: 'horizontal',
            bottom: 0,
            formatter: (name) => name.replace('Dataset ', '')
        }
    };

    return new BaseChart(option);
}

onMounted(() => {
    nextTick(async () => {
        const metricsData = await fetchMetrics();
        const metricsKeyForSum = Object.keys(metricsData).find(i => metricsData[i]?.data_points[0]?.sum)
        const metricsKeysForHistogram = Object.keys(metricsData).filter(i => metricsData[i]?.data_points[0]?.histogram)
        const lineChartData = metricsData[metricsKeyForSum]

        if (lineChartRef.value) {
            // Extract timestamps and convert them to readable format
            const timestamps = lineChartData.data_points.map(point => {
                const date = new Date(parseInt(point.sum.timeUnixNano) / 1000000);
                return date.toLocaleTimeString();
            });

            // Extract the asInt values (all zeros in this case)
            const values = lineChartData.data_points.map(point => parseInt(point.sum.asInt));
            // Set chart options
            const options = {
                container: lineChartRef.value.id,
                // title: 'Active HTTP Server Requests',
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: timestamps,
                    axisLabel: {
                        rotate: 45,
                        interval: 'auto'
                    }
                },
                yAxis: {
                    type: 'value',
                    name: 'Requests',
                    min: 0,
                    max: Math.max(...values) + 1
                },
                series: [{
                    name: 'Requests',
                    type: 'line',
                    data: values,
                    smooth: true
                }]
            };
            // Set the chart options and render
            lineChart = new BaseChart(options)
        }
        if (histogramChartRef0.value) {
            // Histogram
            const histogramData = metricsKeysForHistogram.map(i => {
                return {
                    ...metricsData[i]
                }
            })

            // Function to initialize charts
            function initHistogramCharts(data) {
                const refs = [histogramChartRef0, histogramChartRef1, histogramChartRef2]
                histogramCharts.value = data.map((item, index) => {
                    const seriesData = processHistogramData(item.data_points)
                    return createHistogramChart(
                        refs[index].value,
                        item.description,
                        item.unit,
                        seriesData
                    )
                })
            }
            initHistogramCharts(histogramData)
        }

    })
})


onBeforeUnmount(() => {
    lineChart?.destroy()
    histogramChart?.destroy()
})

</script>