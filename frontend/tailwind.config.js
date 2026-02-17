/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        whola: {
          primary: '#004A8F',   // Azul Mercantil aprox
          dark: '#003366',      // Azul oscuro navegación
          accent: '#009CDE',    // Azul claro (Cian) para botones secundarios
          orange: '#FF7900',    // Naranja para acciones (Pagos/Llamadas)
          gray: '#F4F6F9',      // Fondo gris muy suave
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'], // Fuente limpia
      }
    },
  },
  plugins: [],
}