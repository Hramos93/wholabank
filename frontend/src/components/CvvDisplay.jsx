// frontend/src/components/CvvDisplay.jsx
import { useState, useEffect, useRef } from 'react';
import { Eye, EyeOff } from 'lucide-react';

// Constante para el tiempo de auto-ocultamiento (15 minutos)
const AUTO_HIDE_TIMEOUT_MS = 15 * 60 * 1000;

/**
 * Componente seguro y accesible para mostrar/ocultar un CVV.
 * @param {{ cvv: string }} props El código CVV a mostrar.
 */
const CvvDisplay = ({ cvv }) => {
    const [isCvvVisible, setIsCvvVisible] = useState(false);
    const timerRef = useRef(null);

    // Efecto para manejar el temporizador de auto-ocultamiento.
    useEffect(() => {
        // Si el CVV se hace visible, iniciar el temporizador.
        if (isCvvVisible) {
            timerRef.current = setTimeout(() => {
                setIsCvvVisible(false);
            }, AUTO_HIDE_TIMEOUT_MS);
        }

        // Función de limpieza: se ejecuta cuando el componente se desmonta
        // o antes de que el efecto se vuelva a ejecutar.
        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
    }, [isCvvVisible]); // Se redispare solo cuando la visibilidad cambia.

    const handleToggleVisibility = () => {
        // Limpiar cualquier temporizador existente al interactuar manualmente.
        if (timerRef.current) {
            clearTimeout(timerRef.current);
        }
        setIsCvvVisible(prev => !prev);
    };

    const CvvIcon = isCvvVisible ? EyeOff : Eye;
    const label = isCvvVisible ? 'Ocultar código de seguridad' : 'Mostrar código de seguridad';

    return (
        <div className="flex items-center gap-2">
            <span 
                aria-live="polite" 
                className="w-8 text-center tracking-widest"
            >
                {isCvvVisible ? cvv : '***'}
            </span>
            <button
                type="button"
                onClick={handleToggleVisibility}
                aria-label={label}
                aria-expanded={isCvvVisible}
                className="text-blue-200 hover:text-white transition-colors"
            >
                <CvvIcon size={16} />
            </button>
        </div>
    );
};

export default CvvDisplay;
