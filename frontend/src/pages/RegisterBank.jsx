// frontend/src/pages/RegisterBank.jsx
import { useState } from 'react';
import api from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import { Building2, Globe, Hash, FileText, ArrowLeft, Save, ShieldCheck } from 'lucide-react';

const RegisterBank = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    
    const [formData, setFormData] = useState({
        nombre: '',
        rif: '',
        codigo: '',
        api_url: 'http://'
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            await api.post('admin/registrar-banco/', formData);
            
            Swal.fire({
                icon: 'success',
                title: 'Banco Registrado',
                text: `Se ha añadido a ${formData.nombre} al directorio de enrutamiento.`,
                confirmButtonColor: '#1e3a8a'
            }).then(() => {
                navigate('/admin'); // Volver al panel admin
            });

        } catch (error) {
            const msg = error.response?.data?.error?.message || 'Error de conexión';
            Swal.fire({ icon: 'error', title: 'Error', text: msg });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-100 font-sans">
            
            {/* Header Admin */}
            <header className="bg-slate-900 text-white shadow-md">
                <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <ShieldCheck className="text-orange-500" size={32} />
                        <div>
                            <h1 className="text-xl font-bold tracking-wider">WHOLA <span className="text-gray-400">ADMIN</span></h1>
                            <p className="text-xs text-gray-400">Registro de Nodos Bancarios</p>
                        </div>
                    </div>
                    <button onClick={() => navigate('/admin')} className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors">
                        <ArrowLeft size={16} /> Cancelar
                    </button>
                </div>
            </header>

            <main className="max-w-2xl mx-auto px-4 py-8">
                
                <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                    <div className="bg-blue-900 p-6 text-white">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Building2 /> Nuevo Aliado Bancario
                        </h2>
                        <p className="text-blue-200 text-sm mt-1">
                            Registra la información técnica para permitir transferencias interbancarias.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="p-8 space-y-6">
                        
                        {/* Nombre y RIF */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1 flex items-center gap-1">
                                    <Building2 size={14} className="text-orange-600"/> Nombre del Banco
                                </label>
                                <input 
                                    type="text" name="nombre"
                                    value={formData.nombre} onChange={handleChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 outline-none"
                                    placeholder="Ej. Banco Central UCV"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1 flex items-center gap-1">
                                    <FileText size={14} className="text-orange-600"/> RIF Jurídico
                                </label>
                                <input 
                                    type="text" name="rif"
                                    value={formData.rif} onChange={handleChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 outline-none uppercase"
                                    placeholder="J-00000000-0"
                                    required
                                />
                            </div>
                        </div>

                        {/* Código y URL */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1 flex items-center gap-1">
                                    <Hash size={14} className="text-orange-600"/> Código Bancario (4 dígitos)
                                </label>
                                <input 
                                    type="text" name="codigo"
                                    value={formData.codigo} onChange={handleChange}
                                    maxLength="4"
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 outline-none font-mono tracking-widest"
                                    placeholder="0002"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1 flex items-center gap-1">
                                    <Globe size={14} className="text-orange-600"/> Endpoint API (URL)
                                </label>
                                <input 
                                    type="url" name="api_url"
                                    value={formData.api_url} onChange={handleChange}
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 outline-none font-mono text-sm"
                                    placeholder="http://192.168.1.XX:8000/api/"
                                    required
                                />
                            </div>
                        </div>

                        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm text-yellow-800">
                            <p className="font-bold">⚠️ Importante:</p>
                            <p>Asegúrate de que la URL termine en <code>/api/</code> y que el otro equipo tenga habilitado CORS para nuestra IP.</p>
                        </div>

                        <button 
                            type="submit" 
                            disabled={loading}
                            className="w-full bg-blue-900 text-white font-bold py-4 rounded-lg shadow-lg hover:bg-blue-800 transition-all active:scale-95 flex justify-center items-center gap-2"
                        >
                            {loading ? 'Registrando...' : <><Save size={20}/> Guardar Banco en Directorio</>}
                        </button>

                    </form>
                </div>
            </main>
        </div>
    );
};

export default RegisterBank;