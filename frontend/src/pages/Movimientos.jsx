import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowDownRight, ArrowUpRight, Calendar } from 'lucide-react';
import api from '../api/axiosConfig';

export default function Movimientos() {
  const navigate = useNavigate();
  const [transacciones, setTransacciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState('TODOS');

  useEffect(() => {
    const fetchMovimientos = async () => {
      try {
        // Obtener el token de seguridad almacenado
        const token = localStorage.getItem('access_token');
        if (!token) {
          navigate('/login'); // Si no está logueado, lo mandamos al login
          return;
        }

        // Petición a tu API usando tu instancia configurada (ya inyecta el token automáticamente)
        const response = await api.get('transacciones/');
        setTransacciones(response.data);
      } catch (error) {
        console.error("Error al obtener movimientos:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMovimientos();
  }, [navigate]);

  // Lógica para los botones de filtros (Todos, Ingresos, Egresos)
  const transaccionesFiltradas = transacciones.filter(t => 
    filtro === 'TODOS' ? true : t.direccion === filtro
  );

  // Función para formatear la fecha estilo "12 oct 2023, 14:30"
  const formatFecha = (fechaString) => {
    const opciones = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(fechaString).toLocaleDateString('es-VE', opciones);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-gray-800">
      {/* --- HEADER --- */}
      <div className="bg-blue-900 text-white px-6 py-6 shadow-md sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <button onClick={() => navigate('/dashboard')} className="p-2 hover:bg-blue-800 rounded-full transition-colors">
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-2xl font-bold">Mis Movimientos</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* --- FILTROS --- */}
        <div className="flex gap-2 mb-8 bg-white p-2 rounded-xl shadow-sm border border-gray-100 overflow-x-auto">
          <button 
            onClick={() => setFiltro('TODOS')}
            className={`px-6 py-2.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all ${filtro === 'TODOS' ? 'bg-blue-100 text-blue-900' : 'text-gray-500 hover:bg-gray-50'}`}
          >
            Todos
          </button>
          <button 
            onClick={() => setFiltro('ENTRANTE')}
            className={`px-6 py-2.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all flex items-center gap-2 ${filtro === 'ENTRANTE' ? 'bg-green-100 text-green-800' : 'text-gray-500 hover:bg-gray-50'}`}
          >
            <ArrowDownRight size={16} /> Ingresos
          </button>
          <button 
            onClick={() => setFiltro('SALIENTE')}
            className={`px-6 py-2.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all flex items-center gap-2 ${filtro === 'SALIENTE' ? 'bg-red-100 text-red-800' : 'text-gray-500 hover:bg-gray-50'}`}
          >
            <ArrowUpRight size={16} /> Egresos
          </button>
        </div>

        {/* --- LISTA DE TRANSACCIONES --- */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900 mx-auto mb-4"></div>
            <p className="text-gray-500">Cargando tus movimientos...</p>
          </div>
        ) : transaccionesFiltradas.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl shadow-sm border border-gray-100">
            <Calendar size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500 text-lg">No hay movimientos para mostrar.</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            {transaccionesFiltradas.map((t, index) => (
              <div key={t.id} className={`p-5 flex items-center justify-between hover:bg-slate-50 transition-colors ${index !== transaccionesFiltradas.length - 1 ? 'border-b border-gray-100' : ''}`}>
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-full ${t.direccion === 'ENTRANTE' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-500'}`}>
                    {t.direccion === 'ENTRANTE' ? <ArrowDownRight size={24} /> : <ArrowUpRight size={24} />}
                  </div>
                  <div>
                    <p className="font-bold text-gray-800 text-base">{t.descripcion}</p>
                    <p className="text-sm font-medium text-blue-900 mt-0.5">{t.detalle_contraparte}</p> {/* AQUÍ MOSTRAMOS EL DESTINO/ORIGEN */}
                    <p className="text-xs text-gray-500 mt-1">{formatFecha(t.fecha)} • Ref: {t.id}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-bold text-lg ${t.direccion === 'ENTRANTE' ? 'text-green-600' : 'text-gray-800'}`}>
                    {t.direccion === 'ENTRANTE' ? '+' : '-'} Bs. {parseFloat(t.monto).toLocaleString('es-VE', { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}