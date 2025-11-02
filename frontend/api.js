import axios from 'axios';

// Función simplificada que prioriza la variable de build
const getApiUrl = () => {
  // 1. Variable de entorno de build (PRIORIDAD PRINCIPAL)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // 2. Desarrollo local (fallback)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // 3. Fallback general (última opción)
  return `${window.location.protocol}//${window.location.hostname}:8000`;
};

const apiClient = axios.create({
  baseURL: getApiUrl(),
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Debug para verificar configuración
console.log('🔗 API Base URL configurada:', getApiUrl());
console.log('🌐 Variable de entorno:', import.meta.env.VITE_API_BASE_URL);

export default {
  async requestCHAT(data) {
    const response = await apiClient.post('/chat/query', data);
    return response.data;
  },
  
  async createSession(userId = "anonymous_user") {
    const response = await apiClient.post('/sessions', { user_id: userId });
    return response.data;
  },
  
  async getSession(sessionId) {
    const response = await apiClient.get(`/sessions/${sessionId}`);
    return response.data;
  },
  
  async clearSessionHistory(sessionId) {
    const response = await apiClient.delete(`/sessions/${sessionId}/history`);
    return response.data;
  }
};
