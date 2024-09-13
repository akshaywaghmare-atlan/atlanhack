<template>
    <div class="flex flex-col w-full h-full px-12 py-8">
        <h1 class="px-4 my-4 text-4xl font-bold">Assets</h1>
        <div class="px-4 mb-4">
            <ul class="flex border-b">
                <li class="mr-1" v-for="tab in tabs" :key="tab">
                    <a :class="[
                        'inline-block py-2 px-4 text-base font-medium cursor-pointer transition-all duration-300 ease-in-out',
                        activeTab === tab
                            ? 'border-b-2 border-blue-500 text-blue-500'
                            : 'text-gray-500 hover:text-gray-700 border-b-2 border-transparent'
                    ]" @click="() => onChangeTab(tab)">
                        {{ tab }}
                    </a>
                </li>
            </ul>
        </div>
        <div class="flex-grow px-8">
            <div v-if="activeTab === 'Viewer'" class="w-full">
                <form @submit.prevent="handleApply" class="flex flex-row items-center justify-between mb-4">
                    <div class="mb-4 basis-[25%]">
                        <label class="block text-sm font-medium text-gray-700">Entity Type</label>
                        <select v-model="entityType"
                            class="block w-full py-2 pl-3 pr-10 mt-1 text-base bg-white border border-blue-600 border-solid rounded-md text-slate-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                            <option value="Table">Table</option>
                            <option value="Column">Column</option>
                        </select>
                    </div>
                    <div class="flex items-end justify-between basis-[20%]">
                        <div class="w-full mr-2">
                            <label class="block text-sm font-medium text-gray-700">Fields</label>
                            <select v-model="selectedFields" @change="e => handleFieldChange(e.target.value)"
                                class="block w-full py-2 pl-3 pr-10 mt-1 text-base bg-white border border-blue-600 border-solid rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                                <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
                            </select>
                        </div>
                        <button type="submit"
                            class="inline-flex justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm h-fit hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Apply
                        </button>
                    </div>
                </form>
                <div v-if="showTable" id="assets-table" class="w-full">

                </div>
            </div>
            <div v-else-if="activeTab === 'Discovery'" class="w-full">
                <!-- Discovery tab content -->
                <p>Discovery content goes here</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import sdk from '../application-ui-sdk/src/index';

const { Table } = sdk;

const tabs = ['Viewer', 'Discovery'];
const activeTab = ref('Viewer');
const entityType = ref('Table');
const columns = ['columns', 'package', 'namespace', 'name', 'displayName'];
const selectedFields = ref([]);
const showTable = ref(false);


const onChangeTab = (tab) => {
    activeTab.value = tab;
};

const handleApply = () => {
    showTable.value = true;
    renderAssetsTable();
};

const renderAssetsTable = () => {
    const cols = columns.map(field => ({
        key: field,
        header: field.charAt(0).toUpperCase() + field.slice(1),
        sorter: (a, b) => {
            if (typeof a[field] === 'string' && typeof b[field] === 'string') {
                return a[field].localeCompare(b[field]);
            } else if (typeof a[field] === 'number' && typeof b[field] === 'number') {
                return a[field] - b[field];
            }
            return 0;
        }
    }));

    // Mock data for demonstration
    const mockData = [
        { columns: 'col1, col2', package: 'pkg1', namespace: 'ns1', name: 'Table1', displayName: 'First Table' },
        { columns: 'col3, col4', package: 'pkg2', namespace: 'ns2', name: 'Table2', displayName: 'Second Table' },
    ];

    new Table('assets-table', {
        columns: cols,
        data: mockData,
        options: {
            scrollable: true,
            searchable: false,
            pageSize: 20,
            onChange: (params) => handleFieldChange(params),
        },
    });
};

const handleFieldChange = (params) => {
    // Handle table changes here

};

onMounted(() => {
    // Any initialization logic can go here
});
</script>