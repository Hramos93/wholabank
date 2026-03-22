import axios from 'axios';

// Creamos una instancia de Axios apuntando al prefijo /api/
const api = axios.create({
    baseURL: '/api/', 
});

// Interceptor: Antes de que salga cualquier petición, le pegamos el Token si existe
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;