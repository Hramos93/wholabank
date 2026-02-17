// frontend/src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import POS from './pages/POS';
import Register from './pages/Register'; // Importamos la nueva página
import AdminPanel from './pages/AdminPanel'; // ruta de administración
import RegisterBank from './pages/RegisterBank';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Página Principal Pública */}
        <Route path="/" element={<Home />} />
        
        {/* Autenticación y Registro */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} /> {/* Nueva Ruta */}
        
        {/* Rutas Privadas / Aplicativos */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/pos" element={<POS />} />

       {/* Ruta de administración */}
      <Route path="/admin" element={<AdminPanel />} />
       {/* RRegistro de banco */}
      <Route path="/admin/register-bank" element={<RegisterBank />} />
       
      </Routes>
    </BrowserRouter>
  )
}

export default App;



