<template>
    <div
        class="flex flex-col w-full p-5 m-4 overflow-y-hidden border-2 border-gray-200 border-solid rounded-lg box-shadow-md">
        <h1 class="px-4 my-4 mb-4 text-4xl font-bold">Telemetry</h1>
        <div class="flex items-center justify-between mx-4 border-b border-gray-200 border-solid">
            <ul class="flex border-b">
                <li class="mr-1" v-for="tab in tabs" :key="tab">
                    <a :class="[
                        'inline-block py-2 px-4 text-lg font-medium cursor-pointer transition-all duration-300 ease-in-out',
                        activeTab === tab
                            ? 'border-b-2 border-blue-500 text-blue-500'
                            : 'text-gray-500 hover:text-gray-700 border-b-2 border-transparent'
                    ]" @click="() => onChangeTab(tab)">
                        {{ tab }}
                    </a>
                </li>
            </ul>
            <button @click="refreshActiveTab"
                class="p-2 ml-4 text-white transition-colors bg-white border border-solid rounded-md border-slate-400 hover:bg-white hover:border-blue-500 hover:shadow-md">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none">
                    <path stroke="#3b82f6" stroke-linecap="round" stroke-linejoin="round" d="M4.99 6.232h-3v-3" />
                    <path stroke="#3b82f6" stroke-linecap="round" stroke-linejoin="round"
                        d="M4.11 11.889a5.5 5.5 0 1 0 0-7.778L1.99 6.232" />
                </svg>
            </button>
        </div>
        <div class="flex-grow overflow-y-auto">
            <div v-if="activeTab === 'Logs'" id="logs-table" class="w-full"></div>
            <div v-else-if="activeTab === 'Traces'" class="w-full px-4" id="traces-table">
            </div>
            <div v-else-if="activeTab === 'Events'" class="w-full px-4" id="events-table">
            </div>
            <div v-else-if="activeTab === 'Metrics'" class="w-full px-4">
                <Metrics />
            </div>
        </div>
    </div>
</template>
<script setup>

import { ref, onMounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router'
import * as sdk from "@atlanhq/application-ui-sdk";
import api from '../api'
import Metrics from '../components/Metrices';

const { Table } = sdk;

const logsData = ref([])
const tracesData = ref([])
const eventsData = ref([])

const tabs = ['Logs', 'Traces', 'Events', 'Metrics']
const activeTab = ref('Logs')

const TracesColumns = [
    {
        key: 'trace_id',
        header: 'Trace ID',
    },
    {
        key: 'start_time',
        header: 'Start Time',
        formatter: (value) => new Date(value).toLocaleString()
    },
    {
        key: 'end_time',
        header: 'End Time',
        formatter: (value) => new Date(value).toLocaleString()
    },
    { key: 'name', header: 'Name' },
    { key: 'span_id', header: 'Span ID' },
];

const EventsColumns = [
    { key: 'name', header: 'Name' },
    { key: 'event_type', header: 'Event Type' },
    { key: 'status', header: 'Status' },
    { key: 'application_name', header: 'Application Name' },
    { key: 'attributes', header: 'Attributes' },
    { key: 'timestamp', header: 'Timestamp' },
    { key: 'observed_timestamp', header: 'Observed Timestamp' },
];

const onChangeTab = (tab) => {
    activeTab.value = tab
    if (tab === 'Logs') {
        renderLogsTable();
    } else if (tab === 'Traces') {
        renderTracesTable()
    } else if (tab === 'Events') {
        renderEventsTable()
    }
}

const refreshActiveTab = () => {
    if (activeTab.value === 'Logs') {
        renderLogsTable();
    } else if (activeTab.value === 'Traces') {
        renderTracesTable();
    } else if (activeTab.value === 'Events') {
        renderEventsTable();
    }
}

const renderEventsTable = async () => {
    await fetchEvents();
    new Table('events-table', {
        columns: EventsColumns,
        data: JSON.parse(JSON.stringify(eventsData.value)),
        options: {
            scrollable: true,
            searchable: true,
            pageSize: 20,
            onChange: (params) => handleEventsChange(params),
        },
    });
}

const fetchEvents = async () => {
    try {
        const payload = {
            keyword: ''
        }
        const response = await api.fetchTelemetryEvents(payload)
        if (response && response.length) {
            eventsData.value = response
        } else {
            eventsData.value = [];
        }
        return eventsData.value
    } catch (error) {
        console.log(error);
        return []
    }
}

const renderLogsTable = async () => {
    await fetchLogs();
    new Table('logs-table', {
        columns,
        data: JSON.parse(JSON.stringify(logsData.value)),
        options: {
            scrollable: true,
            searchable: true,
            pageSize: 20,
            onChange: (params) => handleChange(params),
        },
    });
}

const renderTracesTable = async () => {
    await fetchTraces();
    new Table('traces-table', {
        columns: TracesColumns,
        data: JSON.parse(JSON.stringify(tracesData.value)),
        options: {
            scrollable: true,
            searchable: true,
            pageSize: 20,
            expandable: true,
            onChange: (params) => handleTracesChange(params),
        },
    });
}

const columns = [
    {
        key: 'severity',
        header: 'Severity',
        formatter: (value) => `
            <div class="flex items-center">
                <span class="${severityColors[value] || 'text-gray-600'} text-base"> ${value} </span>
            </div>
        `,
    },
    {
        key: 'observed_timestamp',
        header: 'Timestamp',
        formatter: (value) => new Date(value).toLocaleString()
    },
    { key: 'body', header: 'Body' },
    { key: 'trace_id', header: 'Trace ID' },
    { key: 'span_id', header: 'Span ID' },
];

const fetchLogs = async () => {
    try {
        const payload = {
            keyword: ''
        }
        const response = await api.fetchTelemetryLogs(payload)
        if (response && response.length) {
            logsData.value = response
        } else {
            logsData.value = [];
        }
        return logsData.value
    } catch (error) {
        console.log(error);
        return []
    }
}

const groupByTraceId = (data) => {
    const groupedData = data.reduce((acc, trace) => {
        if (!acc[trace.trace_id]) {
            acc[trace.trace_id] = {
                trace_id: trace.trace_id,
                spans: [],
                start_time: new Date(trace.start_time).toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true }),
                end_time: new Date(trace.end_time).toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true }),
                name: trace.name,
                span_id: trace.span_id,
            };
        }
        acc[trace.trace_id].spans.push(trace);

        // Update start_time and end_time for the trace
        acc[trace.trace_id].start_time = new Date(Math.min(new Date(acc[trace.trace_id].start_time), new Date(trace.start_time)));
        acc[trace.trace_id].end_time = new Date(Math.max(new Date(acc[trace.trace_id].end_time), new Date(trace.end_time)));

        return acc;
    }, {});

    // Convert the grouped object to an array and sort by start_time
    return Object.values(groupedData).sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
};

const fetchTraces = async () => {
    try {
        const payload = {
            keyword: ''
        }
        const response = await api.fetchTelemetryTraces(payload)
        if (response && response.length) {
            tracesData.value = groupByTraceId(response)
            console.log(tracesData.value, "<-- tracesData.value");
        } else {
            tracesData.value = [];
        }
        return tracesData.value
    } catch (error) {
        console.log(error);
        return []
    }
}

const handleChange = async ({ key, value }) => {
    const payload = {
        keyword: value
    }
    switch (key) {
        case 'search':
            const response = await api.fetchTelemetryLogs(payload);
            console.log(response, "<---- search response");
            logsData.value = response || [];
        default:
            break;
    }

    new Table('logs-table', {
        columns,
        data: JSON.parse(JSON.stringify(logsData.value)),
        options: {
            scrollable: true,
            searchable: true,
            pageSize: 20,
            onChange: (params) => handleChange(params),
        },
    });
    return JSON.parse(JSON.stringify(logsData.value))
}

const handleTracesChange = async ({ key, value }) => {
    const payload = {
        keyword: value
    }
    const response = await api.fetchTelemetryTraces(payload);
    // console.log(response, "<---- search response");
    tracesData.value = response || [];

    new Table('traces-table', {  // Changed from 'logs-table' to 'traces-table'
        columns: TracesColumns,  // Changed from 'columns' to 'TracesColumns'
        data: JSON.parse(JSON.stringify(tracesData.value)),
        options: {
            scrollable: true,
            searchable: true,
            pageSize: 20,
            expandable: true,
            onChange: (params) => handleTracesChange(params),
        },
    });
    return JSON.parse(JSON.stringify(tracesData.value))  // Changed from logsData to tracesData
}

const handleEventsChange = async ({ key, value }) => {
    const payload = {
        keyword: value || ''
    }
    const response = await api.fetchTelemetryEvents(payload);
    eventsData.value = response || [];

    new Table('events-table', {
        columns: EventsColumns,
        data: JSON.parse(JSON.stringify(eventsData.value)),
        options: {
            scrollable: true,
            searchable: true,
            pageSize: 20,
            expandable: true,
            onChange: (params) => handleEventsChange(params),
        },
    });
    return JSON.parse(JSON.stringify(eventsData.value))
}

onMounted(() => {
    nextTick(async () => {
        await renderLogsTable();
    });
});

// Add a watch effect to re-render the table when activeTab changes to 'Logs'
watch(activeTab, (newTab) => {
    if (newTab === 'Logs') {
        renderLogsTable();
    }
    if (newTab === 'Traces') {
        renderTracesTable();
    }
});

const severityColors = {
    'DEBUG': 'text-gray-600',
    'INFO': 'text-blue-500',
    'WARNING': 'text-yellow-500',
    'ERROR': 'text-red-400',
    'CRITICAL': 'text-red-500'
}

</script>
