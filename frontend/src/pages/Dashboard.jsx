// frontend/src/pages/Dashboard.jsx
import { useEffect, useState } from 'react';
import api from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import { 
    LogOut, CreditCard, DollarSign, Activity, 
    ChevronRight, Wallet, ArrowUpRight, ArrowDownLeft 
} from 'lucide-react';

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('dashboard/');
                setData(response.data);
            } catch (error) {
                if (error.response?.status === 401) navigate('/login');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [navigate]);

    if (loading) return (
        <div className="h-screen flex items-center justify-center bg-slate-100 text-blue-900">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div>
        </div>
    );

    if (!data) return null;

    return (
        <div className="min-h-screen bg-slate-100 font-sans">
            
            {/* === NAVBAR === */}
            <nav className="bg-blue-900 text-white shadow-lg sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <div className="bg-white/10 p-1.5 rounded text-xl font-black italic">W</div>
                            <span className="font-bold tracking-tight text-lg">WHOLA <span className="font-light opacity-80">EN LÍNEA</span></span>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-sm font-medium hidden sm:block">
                                Hola, {data.nombre_usuario}
                            </span>
                            <button 
                                onClick={() => { localStorage.clear(); navigate('/'); }}
                                className="bg-red-500/20 hover:bg-red-600 text-red-100 hover:text-white p-2 rounded-full transition-all"
                                title="Cerrar Sesión"
                            >
                                <LogOut size={18} />
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* === CONTENIDO PRINCIPAL === */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                
                {/* Saludo y Fecha */}
                <header className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-800">Resumen Financiero</h1>
                    <p className="text-gray-500 text-sm">Consulta tus productos y movimientos</p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* === COLUMNA IZQUIERDA (Cuentas y Tarjetas) === */}
                    <div className="lg:col-span-2 space-y-6">
                        
                        {data.cuentas.map((cuenta) => (
                            <div key={cuenta.numero_cuenta} className="space-y-6">
                                
                                {/* Tarjeta de Saldo (Cuenta) */}
                                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 flex flex-col sm:flex-row justify-between items-center gap-4">
                                    <div className="flex items-center gap-4 w-full">
                                        <div className="bg-blue-100 p-3 rounded-full text-blue-900">
                                            <Wallet size={24} />
                                        </div>
                                        <div>
                                            {/* Tarjeta de Saldo (Cuenta) */}
                                            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 flex flex-col sm:flex-row justify-between items-center gap-4">
                                                <div className="flex items-center gap-4 w-full">
                                                    <div className={`p-3 rounded-full ${cuenta.tipo_cuenta === 'CORRIENTE' ? 'bg-blue-100 text-blue-900' : 'bg-green-100 text-green-900'}`}>
                                                        <Wallet size={24} />
                                                    </div>
                                                    <div>
                                                        {/* AQUÍ USAMOS EL DATO DINÁMICO */}
                                                        <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">
                                                            Cuenta {cuenta.tipo_texto || 'Corriente'}
                                                        </p>
                                                        <p className="text-gray-800 font-mono text-sm">{cuenta.numero_cuenta}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right w-full sm:w-auto">
                                                    <p className="text-gray-400 text-xs mb-1">Saldo Disponible</p>
                                                    <p className="text-3xl font-bold text-blue-900">Bs. {cuenta.saldo}</p>
                                                </div>
                                            </div> 
                                            <p className="text-gray-800 font-mono text-sm">{cuenta.numero_cuenta}</p>
                                        </div>
                                    </div>
                                    <div className="text-right w-full sm:w-auto">
                                        <p className="text-gray-400 text-xs mb-1">Saldo Disponible</p>
                                        <p className="text-3xl font-bold text-blue-900">Bs. {cuenta.saldo}</p>
                                    </div>
                                </div>

                                {/* Tarjetas Asociadas (Visual) */}
                                <h3 className="text-gray-600 font-bold text-sm ml-1">Tarjetas Asociadas</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {cuenta.tarjetas.map((t) => (
                                        <div key={t.numero} className="relative h-48 rounded-2xl shadow-xl overflow-hidden text-white transition-transform hover:-translate-y-1 duration-300">
                                            {/* Fondo Gradiente estilo Visa/Mastercard */}
                                            <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-blue-800 to-blue-600"></div>
                                            
                                            {/* Patrón Decorativo (Círculos) */}
                                            <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
                                            <div className="absolute bottom-10 left-10 w-20 h-20 bg-cyan-400/20 rounded-full blur-xl"></div>

                                            {/* Contenido de la Tarjeta */}
                                            <div className="relative p-6 h-full flex flex-col justify-between z-10">
                                                <div className="flex justify-between items-start">
                                                    {/* Chip Simulado */}
                                                    <div className="w-10 h-8 bg-yellow-200/80 rounded-md border border-yellow-400/50 flex items-center justify-center">
                                                        <div className="grid grid-cols-2 gap-0.5 w-6">
                                                            <div className="border border-yellow-600/30 h-3"></div>
                                                            <div className="border border-yellow-600/30 h-3"></div>
                                                        </div>
                                                    </div>
                                                    <span className="font-bold italic tracking-wider">WHOLA</span>
                                                </div>

                                                <div className="space-y-4">
                                                    <p className="font-mono text-xl tracking-widest shadow-black drop-shadow-md">
                                                        {t.numero.match(/.{1,4}/g).join(' ')}
                                                    </p>
                                                    <div className="flex justify-between text-xs font-mono uppercase text-blue-100">
                                                        <div>
                                                            <span className="block text-[10px] opacity-70">Vence</span>
                                                            {t.fecha_vencimiento}
                                                        </div>
                                                        <div>
                                                            <span className="block text-[10px] opacity-70">CVC</span>
                                                            ***
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* === COLUMNA DERECHA (Accesos Rápidos) === */}
                    <div className="space-y-6">
                        
                        {/* Menú de Acciones */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
                            <h3 className="text-gray-800 font-bold mb-4">Operaciones Rápidas</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <QuickAction icon={<ArrowUpRight size={20}/>} text="Transferir" color="bg-cyan-100 text-cyan-700" />
                                <QuickAction icon={<CreditCard size={20}/>} text="Pagar TC" color="bg-orange-100 text-orange-700" />
                                <QuickAction icon={<DollarSign size={20}/>} text="Pago Móvil" color="bg-green-100 text-green-700" />
                                <QuickAction icon={<Activity size={20}/>} text="Movimientos" color="bg-purple-100 text-purple-700" />
                            </div>
                        </div>

                        {/* Banner Publicitario Interno */}
                        <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-6 text-white shadow-md">
                            <p className="font-bold text-lg mb-2">¡Aumenta tu límite!</p>
                            <p className="text-sm opacity-90 mb-4">Solicita hoy mismo un incremento en tu Tarjeta de Crédito Whola.</p>
                            <button className="bg-white text-orange-600 text-xs font-bold py-2 px-4 rounded-full shadow hover:bg-gray-50 transition-colors">
                                Solicitar ahora
                            </button>
                        </div>

                    </div>

                </div>
            </main>
        </div>
    );
};

// Componente pequeño para botones de acción rápida
const QuickAction = ({ icon, text, color }) => (
    <button className="flex flex-col items-center justify-center gap-2 p-4 rounded-xl border border-gray-100 hover:bg-gray-50 hover:border-gray-200 transition-all active:scale-95 group">
        <div className={`p-3 rounded-full ${color} group-hover:scale-110 transition-transform`}>
            {icon}
        </div>
        <span className="text-xs font-semibold text-gray-600">{text}</span>
    </button>
);

export default Dashboard;