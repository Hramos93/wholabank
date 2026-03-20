// frontend/src/api/axiosConfig.js
import axios from 'axios';

// 1. Obtenemos la URL del entorno
const rawApiUrl = import.meta.env.DEV ? '/api/' : (import.meta.env.VITE_API_URL || '/api/');

// 2. BLINDAJE: Aseguramos que la base SIEMPRE termine en '/'
const safeBaseURL = rawApiUrl.endsWith('/') ? rawApiUrl : `${rawApiUrl}/`;

const api = axios.create({
    baseURL: safeBaseURL,
    headers: {
        'Content-Type': 'application/json',
    }
});

// INTERCEPTOR: Se ejecuta antes de cada petición
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        
        // Solo añade el token si existe Y la URL no es la de registro.
        // Convertimos a string por seguridad antes de usar .includes()
        const urlString = config.url ? config.url.toString() : '';
        
        if (token && !urlString.includes('registro/')) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;