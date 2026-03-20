// frontend/src/components/ClaimBonusButton.jsx
import { useState } from 'react';
import api from '../api/axiosConfig';
import Swal from 'sweetalert2';
import { Gift } from 'lucide-react';
import Confetti from 'react-confetti';
import { useWindowSize } from 'react-use';

const ClaimBonusButton = ({ onBonusClaimed }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false);
    const { width, height } = useWindowSize();

    const handleClaim = async () => {
        setIsLoading(true);
        try {
            await api.post('reclamar-bono/');
            
            setShowConfetti(true);
            
            Swal.fire({
                icon: 'success',
                title: '¡1,000 Bs. Desbloqueados!',
                text: '¡El dinero ya está en tu cuenta! ¿Quieres ganar Bs. 500 adicionales? Invita a un amigo a WholaBank.',
                confirmButtonColor: '#1e3a8a',
                confirmButtonText: '¡Genial!'
            }).then(() => {
                onBonusClaimed();
            });

            setTimeout(() => {
                setShowConfetti(false);
            }, 6000);

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
        <>
            {showConfetti && <Confetti width={width} height={height} numberOfPieces={400} gravity={0.15} zIndex={9999} />}

            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-lg border border-green-400 my-6 animate-fade-in-up relative overflow-hidden">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
                
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 relative z-10">
                    <div className="flex items-center gap-4">
                        <Gift size={40} className="text-white drop-shadow-md" />
                        <div>
                            <h3 className="font-bold text-xl tracking-wide">¡Tu regalo de bienvenida!</h3>
                            <p className="text-sm text-green-100 font-medium">Oferta exclusiva válida por tus primeras 24 horas.</p>
                        </div>
                    </div>
                    
                    <button
                        onClick={handleClaim}
                        disabled={isLoading}
                        className="w-full sm:w-auto bg-white text-green-700 font-extrabold py-3 px-8 rounded-full shadow-xl hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100 flex items-center justify-center gap-2"
                    >
                        {isLoading ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-700"></div>
                        ) : (
                            'Desbloquear mis Bs. 1,000'
                        )}
                    </button>
                </div>
            </div>
        </>
    );
};

export default ClaimBonusButton;