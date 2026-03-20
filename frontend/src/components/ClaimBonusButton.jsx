// frontend/src/components/ClaimBonusButton.jsx
import { useState } from 'react';
import api from '../api/axiosConfig';
import Swal from 'sweetalert2';
import { Gift } from 'lucide-react';
// Importamos la magia del confeti y la herramienta para medir la pantalla
import Confetti from 'react-confetti';
import { useWindowSize } from 'react-use';

const ClaimBonusButton = ({ onBonusClaimed }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false); // Estado para controlar el confeti
    const { width, height } = useWindowSize(); // Medimos la pantalla del usuario

    const handleClaim = async () => {
        setIsLoading(true);
        try {
            await api.post('reclamar-bono/');
            
            // ¡Encendemos el confeti!
            setShowConfetti(true);
            
            // Notificación de éxito con Growth Loop (Referidos)
            Swal.fire({
                icon: 'success',
                title: '¡1,000 Bs. Desbloqueados!',
                text: '¡El dinero ya está en tu cuenta! ¿Quieres ganar Bs. 500 adicionales? Invita a un amigo a WholaBank.',
                confirmButtonColor: '#1e3a8a', // Azul de WholaBank
                confirmButtonText: '¡Genial!'
            }).then(() => {
                // Actualizamos la interfaz después de que el usuario cierre la alerta
                onBonusClaimed();
            });

            // Apagamos el confeti mágicamente después de 6 segundos
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
            {/* Si showConfetti es true, hacemos que llueva dinero virtual */}
            {showConfetti && <Confetti width={width} height={height} numberOfPieces={400} gravity={0.15} zIndex={9999} />}

            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-lg border border-green-400 my-6 animate-fade-in-up relative overflow-hidden">
                
                {/* Elementos decorativos de fondo para que el botón se vea premium */}
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
                
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 relative z-10">
                    <div className="flex items-center gap-4">
                        <Gift size={40} className="text-white drop-shadow-md" />
                        <div>
                            {