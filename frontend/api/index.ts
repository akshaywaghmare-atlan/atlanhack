import ApiClient from './apiClient';

const urls = {
    preflight: '/workflows/preflight-check',
    testAuthentication: '/workflows/test-authentication',
    login: '/login',
    logout: '/logout',
    runWorkflow: '/workflows/start-workflow',
    events: '/events',
    telemetry: {
        logs: '/telemetry/v1/logs',
        metrics: '/telemetry/v1/metrics',
        traces: '/telemetry/v1/traces',
    }
}

const apiClient = new ApiClient()

const api = {
    preflight: async (payload: any) => {
        const response = await apiClient.post(urls.preflight, payload);
        return response.json();
    },

    fetchTelemetryLogs: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.logs}?skip=${0}&limit=${limit}&keyword=${keyword}`);
        return response;
    },

    fetchTelemetryTraces: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.traces}?skip=${0}&limit=${limit}`);
        return response;
    },

    fetchTelemetryMetrics: async (payload: any) => {
        const { keyword, limit = 100 } = payload;
        const response = await apiClient.get(`${urls.telemetry.metrics}?skip=${0}&limit=${limit}`);
        return response;
    },

};

export default api;