// frontend/src/services/api.js
import axios from 'axios';

// Point this to your Flask backend
const API_URL = 'http://127.0.0.1:5000/api'; 

const api = axios.create({
    baseURL: API_URL,
});

// Automatically attach the JWT token to every request if it exists
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;