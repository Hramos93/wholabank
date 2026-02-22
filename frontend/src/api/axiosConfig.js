// frontend/src/api/axiosConfig.js

import axios from 'axios';

// Creamos una instancia centralizada de Axios LOCALLLLL
//const api = axios.create({
//    baseURL: 'http://127.0.0.1:8000/api/', // La URL de tu Django
//    headers: {
//        'Content-Type': 'application/json',
//    }
//});

const api = axios.create({
    // Usa la variable de entorno VITE_API_URL para la URL base de la API.
    // En producción, esta variable debe contener la URL del backend en Azure.
    // En desarrollo, se usará la URL del archivo .env.
    baseURL: import.meta.env.VITE_API_URL || '/api/',
    headers: {
        'Content-Type': 'application/json',
    }
});


// INTERCEPTOR: Se ejecuta antes de cada petición
// Su función es inyectar el Token automáticamente si existe.
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            // Si hay token, lo agregamos al header Authorization
            // Formato estándar: "Bearer <token>"
            config.headers.Authorization = `Bearer ${token}`;
        }
return config;
  }
);

// AGREGA ESTA LÍNEA AL FINAL:
export default api;