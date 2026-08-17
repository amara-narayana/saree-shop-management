import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  
  register: async (username: string, email: string, password: string, role: string) => {
    const response = await apiClient.post('/auth/register', {
      username,
      email,
      password,
      role,
    });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
};

export const sareeService = {
  getAll: async (params?: { page?: number; limit?: number; search?: string }) => {
    const response = await apiClient.get('/sarees', { params });
    return response.data;
  },
  
  getById: async (id: number) => {
    const response = await apiClient.get(`/sarees/${id}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await apiClient.post('/sarees', data);
    return response.data;
  },
  
  update: async (id: number, data: any) => {
    const response = await apiClient.put(`/sarees/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    const response = await apiClient.delete(`/sarees/${id}`);
    return response.data;
  },
};

export const intelligenceService = {
  getInventoryAging: async () => {
    const response = await apiClient.get('/intelligence/inventory/aging');
    return response.data;
  },
  
  getDeadStock: async () => {
    const response = await apiClient.get('/intelligence/inventory/dead-stock');
    return response.data;
  },
  
  getReorderRecommendations: async () => {
    const response = await apiClient.get('/intelligence/reorder/recommendations');
    return response.data;
  },
  
  getDashboardSummary: async () => {
    const response = await apiClient.get('/intelligence/dashboard/summary');
    return response.data;
  },
  
  getCustomerSegments: async () => {
    const response = await apiClient.get('/intelligence/customers/segments');
    return response.data;
  },
};

export const saleService = {
  getAll: async (params?: { page?: number; limit?: number }) => {
    const response = await apiClient.get('/sales', { params });
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await apiClient.post('/sales', data);
    return response.data;
  },
  
  getById: async (id: number) => {
    const response = await apiClient.get(`/sales/${id}`);
    return response.data;
  },
};

export default apiClient;
