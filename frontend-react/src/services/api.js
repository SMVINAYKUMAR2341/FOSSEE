import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  login: (username, password) => 
    api.post('/login/', { username, password }),
  
  register: (username, password, email) => 
    api.post('/register/', { username, password, email }),
  
  logout: () => 
    api.post('/logout/'),
  
  getUserInfo: () => 
    api.get('/user/'),
};

// Dataset APIs
export const datasetAPI = {
  uploadCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload-csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes timeout for ML training
    });
  },
  
  getHistory: () => 
    api.get('/history/'),
  
  getDatasetDetail: (id) => 
    api.get(`/dataset/${id}/`),
  
  generateReport: (datasetId = null) => {
    const url = datasetId ? `/generate-report/?dataset_id=${datasetId}` : '/generate-report/';
    return api.get(url, {
      responseType: 'blob',
    });
  },

  deleteDataset: (id) =>
    api.delete(`/dataset/${id}/delete/`),
    
  predictParameters: (equipment_type) =>
    api.post('/predict/', { equipment_type }),
    
  getAllPredictions: () =>
    api.get('/predictions/'),
};

export default api;
