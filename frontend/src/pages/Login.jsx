// frontend/src/pages/Login.jsx
import { useState } from 'react';
import api from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Lock, Loader2 } from 'lucide-react'; // Iconos nuevos

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // La API ahora devuelve { access, refresh, is_admin, username }
            const response = await api.post('token/', { username, password });
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);

            // ===== LÓGICA DE REDIRECCIÓN INTELIGENTE =====
            if (response.data.is_admin) {
                // Si es admin, lo mandamos a su panel de React
                navigate('/admin'); 
            } else {
                navigate('/dashboard'); // Si es cliente, al dashboard normal
            }
        } catch (err) {
            console.error(err);
            setError('Usuario o contraseña incorrectos.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
            
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
                
                {/* Encabezado Azul */}
                <div className="bg-blue-900 p-8 text-center relative">
                    <button 
                        onClick={() => navigate('/')} 
                        className="absolute top-4 left-4 text-blue-200 hover:text-white transition-colors flex items-center gap-1 text-sm font-medium"
                    >
                        <ArrowLeft size={16} /> Volver
                    </button>
                    <div className="bg-white/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 backdrop-blur-sm text-white">
                        <Lock size={32} />
                    </div>
                    <h2 className="text-2xl font-bold text-white">Whola en Línea</h2>
                    <p className="text-blue-200 text-sm">Acceso seguro a tu banca digital</p>
                </div>

                {/* Formulario */}
                <div className="p-8 pt-6">
                    {error && (
                        <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded text-sm text-red-700">
                            <p className="font-bold">Error de acceso</p>
                            <p>{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleLogin} className="space-y-6">
                        {/* Input Usuario */}
                        <div className="space-y-1">
                            <label className="text-sm font-bold text-gray-600 ml-1">Usuario</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400 group-focus-within:text-blue-900">
                                    <User size={20} />
                                </div>
                                <input 
                                    type="text"
                                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 transition-all sm:text-sm"
                                    placeholder="Ingresa tu usuario"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Input Contraseña */}
                        <div className="space-y-1">
                            <label className="text-sm font-bold text-gray-600 ml-1">Contraseña</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400 group-focus-within:text-blue-900">
                                    <Lock size={20} />
                                </div>
                                <input 
                                    type="password"
                                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 transition-all sm:text-sm"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Botón */}
                        <button 
                            type="submit" 
                            disabled={loading}
                            className="w-full flex justify-center items-center gap-2 bg-blue-900 hover:bg-blue-800 text-white font-bold py-3 px-4 rounded-lg shadow-md transition-all active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="animate-spin" /> : 'Ingresar a mi cuenta'}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <a href="#" className="text-sm text-gray-500 hover:text-blue-900 font-medium">
                            ¿Olvidaste tu contraseña?
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;