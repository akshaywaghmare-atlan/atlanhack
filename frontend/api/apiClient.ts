class ApiClient {
    private baseUrl: string;
    private defaultHeaders: HeadersInit;

    constructor() {
        // Extract the base URL from window.location.origin
        this.baseUrl = window?.location.origin || 'http://0.0.0.0:8000';

        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    private async request(endpoint: string, options: RequestInit): Promise<any> {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = { ...this.defaultHeaders, ...options.headers };
        const config = { ...options, headers };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Check if the response is JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    public async get(endpoint: string, params: Record<string, string> = {}): Promise<any> {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        return this.request(url.pathname + url.search, { method: 'GET' });
    }

    public async post(endpoint: string, data: any): Promise<any> {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    public async put(endpoint: string, data: any): Promise<any> {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    public async delete(endpoint: string): Promise<any> {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // public setAuthToken(token: string): void {
    //     this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    // }

    // public clearAuthToken(): void {
    //     delete this.defaultHeaders['Authorization'];
    // }
}

export default ApiClient