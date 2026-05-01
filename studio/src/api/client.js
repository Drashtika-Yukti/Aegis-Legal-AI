import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s timeout for complex legal queries
});

// Interceptor for professional error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Aegis Engine Error:', error);
    if (!error.response) {
      return Promise.reject({
        message: 'Engine Connection Error: Please ensure the Aegis backend is reachable.',
        status: 'offline'
      });
    }
    return Promise.reject({
      message: error.response.data?.detail || 'An unexpected error occurred during reasoning.',
      status: error.response.status
    });
  }
);

export const chatService = {
  async sendMessage(query, sessionId = 'default_session') {
    const response = await apiClient.post('/chat', {
      query,
      session_id: sessionId
    });
    return response.data;
  }
};

export default apiClient;
