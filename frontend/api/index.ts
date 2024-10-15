import ApiClient from './apiClient';

const urls = {
    preflight: '/workflows/v1/check',
    testAuthentication: '/workflows/v1/auth',
    fetchMetadata: '/workflows/v1/metadata',
    login: '/login',
    logout: '/logout',
    runWorkflow: '/workflows/v1/start',
    events: '/events',
    telemetry: {
        logs: '/telemetry/v1/logs',
        metrics: '/telemetry/v1/metrics',
        traces: '/telemetry/v1/traces',
        events: '/telemetry/v1/events',
    }
}

const apiClient = new ApiClient()

const api = {
    testConnection: async (payload: any) => {
        const response = await apiClient.post(urls.testAuthentication, payload);
        return response;
    },

    fetchFilterMetaData: async (payload: any) => {
        const response = await apiClient.post(urls.fetchMetadata, payload);
        return response;
    },

    preflight: async (payload: any) => {
        const response = await apiClient.post(urls.preflight, payload);
        return response;
    },

    fetchTelemetryLogs: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.logs}?skip=${0}&limit=${limit}&body__contains=${keyword}`);
        return response;
    },

    fetchTelemetryTraces: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.traces}?skip=${0}&limit=${limit}&body__contains=${keyword}`);
        return response;
    },

    fetchTelemetryMetrics: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.metrics}?skip=${0}&limit=${limit}&body__contains=${keyword}`);
        return response;
    },

    fetchTelemetryEvents: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.events}?skip=${0}&limit=${limit}&body__contains=${keyword}`);
        return response;
    },

    runWorkflow: async (payload: any) => {
        const response = await apiClient.post(`${urls.runWorkflow}`, payload);
        return response;
    },

};

export default api;