// frontend/src/pages/AdminPanel.jsx
import { useEffect, useState } from 'react';
import api from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';
import { 
    LayoutDashboard, Server, Users, DollarSign, 
    ArrowLeft, ShieldCheck, Globe, Building 
} from 'lucide-react';

const AdminPanel = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchAdminData = async () => {
            try {
                const response = await api.get('admin-panel/');
                setData(response.data);
            } catch (error) {
                console.error("Acceso denegado", error);
                // Si no es admin (403) o no está logueado (401), sacar
                navigate('/dashboard'); 
            } finally {
                setLoading(false);
            }
        };
        fetchAdminData();
    }, [navigate]);

    if (loading) return <div className="h-screen flex items-center justify-center">Cargando panel...</div>;
    if (!data) return null;

    return (
        <div className="min-h-screen bg-slate-100 font-sans">
            
            {/* Header Admin */}
            <header className="bg-slate-900 text-white shadow-md">
                <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <ShieldCheck className="text-orange-500" size={32} />
                        <div>
                            <h1 className="text-xl font-bold tracking-wider">WHOLA <span className="text-gray-400">ADMIN</span></h1>
                            <p className="text-xs text-gray-400">Panel de Control Centralizado</p>
                        </div>
                    </div>
                    <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors">
                        <ArrowLeft size={16} /> Volver a Banca
                    </button>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">

                {/* KPI CARDS (Métricas) */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <KpiCard icon={<Users/>} title="Clientes Totales" value={data.stats.total_clientes} color="bg-blue-600" />
                    <KpiCard icon={<DollarSign/>} title="Liquidez Banco" value={`Bs. ${data.stats.liquidez_total.toLocaleString()}`} color="bg-green-600" />
                    <KpiCard icon={<Server/>} title="Bancos Conectados" value={data.stats.total_bancos_conectados} color="bg-purple-600" />
                    <KpiCard icon={<Globe/>} title="Comercios Externos" value={data.stats.total_comercios_externos} color="bg-orange-600" />
                </div>

                {/* SECCIÓN 1: Directorio del Ecosistema (LO QUE PEDISTE) */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                        <h2 className="font-bold text-gray-800 flex items-center gap-2">
                            <Globe size={20} className="text-blue-900"/> Ecosistema Externo (Directorio)
                        </h2>


                        <div className="flex gap-2">
                            <button 
                                onClick={() => navigate('/admin/register-bank')}
                                className="bg-blue-900 hover:bg-blue-800 text-white text-xs font-bold px-3 py-2 rounded-lg flex items-center gap-1 transition-colors"
                            >
                                + Registrar Banco
                            </button>
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-2 rounded-full font-bold flex items-center">
                                Nodos: {data.directorio.length}
                                </span>
                        </div>

                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-bold">
                            Nodos Detectados: {data.directorio.length}
                        </span>
                    </div>
                    
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-100 text-gray-600 uppercase text-xs font-bold">
                                <tr>
                                    <th className="px-6 py-3">Código</th>
                                    <th className="px-6 py-3">Entidad</th>
                                    <th className="px-6 py-3">Tipo</th>
                                    <th className="px-6 py-3">Endpoint (API)</th>
                                    <th className="px-6 py-3">Estado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {data.directorio.map((nodo) => (
                                    <tr key={nodo.codigo} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 font-mono font-bold text-gray-700">{nodo.codigo}</td>
                                        <td className="px-6 py-4 font-bold text-blue-900">{nodo.nombre}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${nodo.tipo === 'BANCO' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'}`}>
                                                {nodo.tipo}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 font-mono text-gray-500 text-xs truncate max-w-xs" title={nodo.api_url}>
                                            {nodo.api_url}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="flex items-center gap-1 text-green-600 text-xs font-bold">
                                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Activo
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                                {data.directorio.length === 0 && (
                                    <tr>
                                        <td colSpan="5" className="px-6 py-8 text-center text-gray-400 italic">
                                            No hay otros equipos registrados en el Directorio.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* SECCIÓN 2: Clientes Registrados */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
                        <h2 className="font-bold text-gray-800 flex items-center gap-2">
                            <Users size={20} className="text-blue-900"/> Clientes Whola
                        </h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-100 text-gray-600 uppercase text-xs font-bold">
                                <tr>
                                    <th className="px-6 py-3">ID (Rif/Cédula)</th>
                                    <th className="px-6 py-3">Cliente</th>
                                    <th className="px-6 py-3">Tipo</th>
                                    <th className="px-6 py-3">Cuentas</th>
                                    <th className="px-6 py-3 text-right">Saldo Total</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {data.clientes.map((cte) => (
                                    <tr key={cte.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 font-mono text-gray-600">{cte.identidad}</td>
                                        <td className="px-6 py-4 font-bold text-gray-800">{cte.nombre}</td>
                                        <td className="px-6 py-4">
                                            {cte.tipo === 'NATURAL' ? 
                                                <span className="flex items-center gap-1 text-blue-600"><Users size={14}/> Natural</span> : 
                                                <span className="flex items-center gap-1 text-gray-600"><Building size={14}/> Empresa</span>
                                            }
                                        </td>
                                        <td className="px-6 py-4">
                                            {cte.cuentas.map(num => (
                                                <div key={num} className="font-mono text-xs text-gray-500">{num}</div>
                                            ))}
                                        </td>
                                        <td className="px-6 py-4 text-right font-bold text-green-700">
                                            Bs. {cte.saldo_total}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </main>
        </div>
    );
};

const KpiCard = ({ icon, title, value, color }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center gap-4">
        <div className={`p-4 rounded-full text-white ${color} shadow-lg`}>
            {icon}
        </div>
        <div>
            <p className="text-gray-500 text-xs font-bold uppercase">{title}</p>
            <p className="text-2xl font-bold text-gray-800">{value}</p>
        </div>
    </div>
);

export default AdminPanel;