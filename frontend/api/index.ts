import axiosClient from './axios';

const urls = {
    preflight: '/preflight/check',
    testAuthentication: '/preflight/test-authentication',
    login: '/login',
    logout: '/logout',
    runWorkflow: '/workflow/start',
}

const api = {
    preflight: async (payload: any) => {
        const response = await axiosClient.post(urls.preflight, payload);
        return response.json();
    }
};

export default api;