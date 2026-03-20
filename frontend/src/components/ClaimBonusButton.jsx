// frontend/src/components/ClaimBonusButton.jsx
import { useState } from 'react';
import api from '../api/axiosConfig';
import Swal from 'sweetalert2';
import { Gift } from 'lucide-react';

const ClaimBonusButton = ({ onBonusClaimed }) => {
    const [isLoading, setIsLoading] = useState(false);

    const handleClaim = async () => {
        setIsLoading(true);
        try {
            await api.post('reclamar-bono/');
            
            // Notificación de éxito
            Swal.fire({
                icon: 'success',
                title: '¡Bono Reclamado!',
                text: 'Hemos añadido 1000 Bs. a tu cuenta principal.',
                confirmButtonColor: '#1e3a8a', // Azul de WholaBank
            });

            // Llamar a la función del padre para actualizar la UI
            onBonusClaimed();

        } catch (error) {
            const errorMessage = error.response?.data?.error || 'No se pudo reclamar el bono.';
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: errorMessage,
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-lg border border-green-400 my-6 animate-fade-in-up">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <Gift size={40} className="text-white/80" />
                    <div>
                        <h3 className="font-bold text-xl">¡Un Regalo te Espera!</h3>
                        <p className="text-sm opacity-90">Reclama tu Bono de Bienvenida de 1000 Bs. ahora mismo.</p>
                    </div>
                </div>
                <button
                    onClick={handleClaim}
                    disabled={isLoading}
                    className="w-full sm:w-auto bg-white text-green-700 font-bold py-3 px-6 rounded-full shadow-md hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:scale-100"
                >
                    {isLoading ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-700"></div>
                    ) : (
                        'Reclamar Mi Bono'
                    )}
                </button>
            </div>
        </div>
    );
};

export default ClaimBonusButton;
