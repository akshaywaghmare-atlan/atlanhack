import axiosClient from './axios';

const urls = {
    preflight: '/workflows/preflight-check',
    testAuthentication: '/workflows/test-authentication',
    login: '/login',
    logout: '/logout',
    runWorkflow: '/workflows/start-workflow',
}

const api = {
    preflight: async (payload: any) => {
        const response = await axiosClient.post(urls.preflight, payload);
        return response.json();
    }
};

export default api;