// frontend/src/components/TransactionHistory.jsx
import { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { ArrowDownLeft, ArrowUpRight, AlertCircle, Clock } from 'lucide-react';

const TransactionHistory = () => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                const response = await api.get('transacciones/');
                setTransactions(response.data);
            } catch (err) {
                setError('No se pudieron cargar los movimientos.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchTransactions();
    }, []);

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-VE', { style: 'currency', currency: 'VES' }).format(amount);
    }

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-VE', { day: '2-digit', month: 'short' }) + ' - ' + date.toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' });
    }

    const TransactionIcon = ({ direccion }) => {
        if (direccion === 'ENTRANTE') {
            return <div className="p-2 bg-green-100 rounded-full text-green-700"><ArrowDownLeft size={16} /></div>;
        }
        return <div className="p-2 bg-red-100 rounded-full text-red-700"><ArrowUpRight size={16} /></div>;
    };

    if (loading) {
        return (
            <div className="text-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-900 mx-auto"></div>
                <p className="text-sm text-gray-500 mt-2">Cargando movimientos...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                <div className="flex items-center">
                    <AlertCircle className="text-yellow-600" size={20} />
                    <div className="ml-3">
                        <p className="text-sm text-yellow-700">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 mt-6">
            <h3 className="text-gray-800 font-bold mb-4">Movimientos Recientes</h3>
            {transactions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <Clock size={24} className="mx-auto mb-2" />
                    <p>No hay movimientos recientes para mostrar.</p>
                </div>
            ) : (
                <ul className="space-y-4">
                    {transactions.map((tx) => (
                        <li key={tx.id} className="flex items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <TransactionIcon direccion={tx.direccion} />
                                <div>
                                    <p className="font-semibold text-gray-800 text-sm">{tx.descripcion}</p>
                                    <p className="text-xs text-gray-500">{formatDate(tx.fecha)}</p>
                                </div>
                            </div>
                            <p className={`font-mono font-semibold text-sm ${tx.direccion === 'ENTRANTE' ? 'text-green-600' : 'text-gray-900'}`}>
                                {tx.direccion === 'ENTRANTE' ? '+' : '-'} {formatCurrency(tx.monto)}
                            </p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default TransactionHistory;
