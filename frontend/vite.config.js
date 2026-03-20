import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Redirige las peticiones del frontend al backend en desarrollo
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },
  // --- CONFIGURACIÓN PARA PRODUCCIÓN ---
  build: {
    // Directorio de salida (por defecto es 'dist', lo dejamos así)
    outDir: 'dist',
    // La clave de la solución: Le decimos a Vite que todos los assets
    // (CSS, JS, imágenes) deben tener el prefijo '/static/' en sus rutas.
    // Esto alinea el build de React con la configuración STATIC_URL de Django.
    base: '/static/',
  }
})
