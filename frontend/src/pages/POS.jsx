// frontend/src/pages/POS.jsx
import { useState } from 'react';
import api from '../api/axiosConfig'; // Usamos tu config de Axios
import Swal from 'sweetalert2'; // Para las alertas bonitas

const POS = () => {
  const [loading, setLoading] = useState(false);
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    numero_tarjeta: '',
    cvc_tarjeta: '',
    fecha_vencimiento_tarjeta: '',
    monto_pagado: '',
    // Datos fijos del comercio (simulados por ahora)
    codigo_identificador_comercio_receptor: 'C001', 
    codigo_banco_comercio_receptor: '0001',
    codigo_banco_emisor_tarjeta: '0001', // Por defecto asumimos que paga alguien de nuestro banco
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Detectar automáticamente el banco por el BIN (Primeros 6 dígitos)
  const handleCardNumberChange = (e) => {
    const val = e.target.value;
    let bancoEmisor = '0001'; // Default nosotros

    // Lógica simple de enrutamiento visual
    if (val.startsWith("500002")) bancoEmisor = "0002";
    if (val.startsWith("500005")) bancoEmisor = "0005";
    
    setFormData({
      ...formData,
      numero_tarjeta: val,
      codigo_banco_emisor_tarjeta: bancoEmisor
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Armamos el JSON tal cual lo pide el protocolo del Sprint 2
    const payload = {
      // ID de transacción más robusto para evitar colisiones. Idealmente, lo genera el backend.
      numero_transaccion: `TX-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      codigo_banco_emisor_tarjeta: formData.codigo_banco_emisor_tarjeta,
      numero_tarjeta: formData.numero_tarjeta,
      cvc_tarjeta: formData.cvc_tarjeta,
      fecha_vencimiento_tarjeta: formData.fecha_vencimiento_tarjeta,
      codigo_banco_comercio_receptor: formData.codigo_banco_comercio_receptor,
      codigo_identificador_comercio_receptor: formData.codigo_identificador_comercio_receptor,
      monto_pagado: parseFloat(formData.monto_pagado)
    };

    try {
      // Llamada al Backend (Endpoint del Sprint 2)
      // Nota: procesar_pago es público, no necesita Header de Auth
      const response = await api.post('procesar_pago/', payload);

      if (response.status === 201) {
        Swal.fire({
          icon: 'success',
          title: '¡Transacción Aprobada!',
          text: `Se han cobrado Bs. ${payload.monto_pagado} exitosamente.`,
          footer: 'Referencia: ' + payload.numero_transaccion
        });
        // Limpiar formulario
        setFormData({...formData, numero_tarjeta: '', cvc_tarjeta: '', monto_pagado: ''});
      }

    } catch (error) {
      console.error(error);
      let mensajeError = "Error de comunicación";
      
      // Mapeo de errores del Backend (Parte 3 del Sprint)
      if (error.response && error.response.data && error.response.data.error) {
        const backendError = error.response.data.error;
        mensajeError = backendError.message; // Mensaje que viene del Python
        
        // Podemos personalizar íconos según el código
        if (backendError.code === 'IERROR_1004') {
             Swal.fire('Saldo Insuficiente', mensajeError, 'warning');
             setLoading(false);
             return;
        }
      }
      
      Swal.fire({
        icon: 'error',
        title: 'Transacción Rechazada',
        text: mensajeError
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-200 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md border-t-8 border-blue-600">
        <h2 className="text-2xl font-bold text-gray-800 text-center mb-6">Punto de Venta Virtual</h2>
        <div className="bg-blue-50 p-3 rounded mb-4 text-sm text-blue-800">
            Comercio: <strong>Supermercado UCV (C001)</strong>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Monto a Cobrar (Bs.)</label>
            <input
              type="number"
              name="monto_pagado"
              value={formData.monto_pagado}
              onChange={handleChange}
              className="w-full p-3 border-2 border-gray-300 rounded-lg text-xl font-bold text-green-700 focus:border-green-500 outline-none"
              placeholder="0.00"
              step="0.01"
              required
            />
          </div>

          <div className="border-t pt-4 mt-4">
            <p className="text-xs text-gray-500 mb-2 uppercase tracking-wide">Datos de la Tarjeta</p>
            
            <div className="mb-3">
                <input
                type="text"
                name="numero_tarjeta"
                value={formData.numero_tarjeta}
                onChange={handleCardNumberChange}
                className="w-full p-3 border border-gray-300 rounded bg-gray-50 tracking-widest"
                placeholder="Número de Tarjeta (16 dígitos)"
                maxLength="16"
                required
                />
            </div>

            <div className="flex gap-4">
                <input
                type="text"
                name="fecha_vencimiento_tarjeta"
                value={formData.fecha_vencimiento_tarjeta}
                onChange={handleChange}
                className="w-1/2 p-3 border border-gray-300 rounded bg-gray-50 text-center"
                placeholder="MM/YY"
                maxLength="5"
                required
                />
                <input
                type="password"
                name="cvc_tarjeta"
                value={formData.cvc_tarjeta}
                onChange={handleChange}
                className="w-1/2 p-3 border border-gray-300 rounded bg-gray-50 text-center"
                placeholder="CVV"
                maxLength="3"
                required
                />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-4 mt-6 rounded-lg text-white font-bold text-lg shadow-lg transition-all ${
                loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl'
            }`}
          >
            {loading ? 'Procesando...' : 'COBRAR AHORA'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default POS;