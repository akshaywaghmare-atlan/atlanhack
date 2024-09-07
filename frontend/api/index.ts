import axiosClient from './axios';

const urls = {
    preflight: '/preflight',
    testAuthentication: '/test-authentication',
    login: '/login',
    logout: '/logout',
    runWorkflow: '/run-workflow',
}

const api = {
    preflight: async (payload: any) => {
        const response = await axiosClient.post(urls.preflight, payload);
        return response.json();
    }
};

export default api;