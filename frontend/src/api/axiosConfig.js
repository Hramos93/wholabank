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
    // Usa la variable de Render en la nube, o localhost si estás programando en casa
    // En producción, el frontend y el backend están en el mismo dominio.
    // La URL base de la API es simplemente '/api/'.
    baseURL: '/api/',
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