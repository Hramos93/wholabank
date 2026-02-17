// frontend/src/pages/Register.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';
import Swal from 'sweetalert2';
import { ArrowRight, Check, Lock, User, Calendar, FileText, AlertCircle, Building2, Briefcase } from 'lucide-react';

const Register = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    // ESTADO PRINCIPAL
    const [formData, setFormData] = useState({
        tipo_persona: 'NATURAL', // 'NATURAL' o 'JURIDICO'
        nombre_completo: '', // O Razón Social
        cedula: '', // Solo Natural
        rif: '', // Auto para natural, Manual para Juridico
        telefono: '',
        fecha_nacimiento: '', // O Fecha Constitución
        lugar_nacimiento: 'Venezuela',
        estado_civil: 'Soltero',
        email: '',
        profesion: 'Computación', // O Rubro
        origen_fondos: 'Ahorro',
        tipo_cuenta: 'CORRIENTE',
        username: '',
        password: ''
    });

    const [passwordStrength, setPasswordStrength] = useState(0);

    // --- MANEJO DE CAMBIOS ---
    const handleChange = (e) => {
        const { name, value } = e.target;
        if (errors[name]) setErrors({...errors, [name]: null});

        let newData = { ...formData, [name]: value };

        // Lógica automática para Persona Natural
        if (formData.tipo_persona === 'NATURAL' && name === 'cedula') {
            newData.rif = value ? `V-${value}` : '';
        }
        
        // Lógica de mayúsculas para RIF Empresa
        if (formData.tipo_persona === 'JURIDICO' && name === 'rif') {
            newData.rif = value.toUpperCase();
        }

        setFormData(newData);
    };

    // --- VALIDACIONES PASO 1 ---
    const validateStep1 = () => {
        let newErrors = {};
        if (formData.nombre_completo.length < 3) newErrors.nombre_completo = "Nombre muy corto";
        
        if (formData.tipo_persona === 'NATURAL') {
            if (formData.cedula.length < 6) newErrors.cedula = "Cédula inválida";
        } else {
            // Validación básica de RIF J-12345678-9
            if (!/^J-\d+-\d$/.test(formData.rif) && !/^G-\d+-\d$/.test(formData.rif)) {
                newErrors.rif = "Formato inválido (Ej: J-12345678-0)";
            }
        }

        if (formData.telefono.length < 10) newErrors.telefono = "Teléfono inválido";
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // --- AUTO-GENERACIÓN DATOS (PASO 2 y 3) ---
    useEffect(() => {
        if (step === 2 && !formData.fecha_nacimiento) {
            // Fecha aleatoria
            const today = new Date();
            const minYear = today.getFullYear() - 50;
            const maxYear = today.getFullYear() - 10;
            const rYear = Math.floor(Math.random() * (maxYear - minYear + 1)) + minYear;
            const rMonth = String(Math.floor(Math.random() * 12) + 1).padStart(2,'0');
            const rDay = String(Math.floor(Math.random() * 28) + 1).padStart(2,'0');
            
            // Email
            const cleanName = formData.nombre_completo.replace(/\s+/g, '.').toLowerCase();
            const emailBase = `${cleanName.slice(0, 20)}@whola.com`; // Cortar si es muy largo

            setFormData(prev => ({
                ...prev,
                fecha_nacimiento: `${rYear}-${rMonth}-${rDay}`,
                email: emailBase,
                // Ajustes por defecto si es empresa
                profesion: prev.tipo_persona === 'JURIDICO' ? 'Comercio General' : 'Computación',
                origen_fondos: prev.tipo_persona === 'JURIDICO' ? 'Ventas' : 'Ahorro',
                tipo_cuenta: 'CORRIENTE' // Empresas suelen usar corriente
            }));
        }
        
        if (step === 3 && !formData.username) {
            const userBase = formData.email.split('@')[0].replace(/[^a-zA-Z0-9]/g, '');
            const rnd = Math.floor(Math.random() * 999);
            setFormData(prev => ({ ...prev, username: `${userBase}${rnd}` }));
        }
    }, [step]);

    const checkPasswordStrength = (pass) => {
        let score = 0;
        if (pass.length > 7) score += 20;
        if (/[A-Z]/.test(pass)) score += 20;
        if (/[a-z]/.test(pass)) score += 20;
        if (/[0-9]/.test(pass)) score += 20;
        if (/[^A-Za-z0-9]/.test(pass)) score += 20;
        setPasswordStrength(score);
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            await api.post('registro/', formData);
            Swal.fire({
                icon: 'success',
                title: 'Registro Exitoso',
                text: 'Bienvenido a Banco Whola',
                confirmButtonColor: '#1e3a8a'
            }).then(() => navigate('/login'));
        } catch (error) {
            const msg = error.response?.data?.error?.message || error.message;
            Swal.fire({ icon: 'error', title: 'Error', text: msg });
        } finally {
            setLoading(false);
        }
    };

    const ErrorMsg = ({ msg }) => msg ? <p className="text-red-500 text-xs mt-1 flex items-center gap-1"><AlertCircle size={12}/> {msg}</p> : null;

    return (
        <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4 font-sans">
            <div className="bg-white w-full max-w-2xl rounded-2xl shadow-xl overflow-hidden flex flex-col">
                
                {/* Header */}
                <div className="bg-blue-900 p-6 text-white flex justify-between items-center">
                    <div>
                        <h2 className="text-2xl font-bold">Registro de Clientes</h2>
                        <p className="text-blue-200 text-sm">Paso {step} de 3</p>
                    </div>
                    {/* Indicador de Tipo */}
                    <div className="bg-white/20 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                        {formData.tipo_persona === 'NATURAL' ? <User size={14}/> : <Building2 size={14}/>}
                        {formData.tipo_persona}
                    </div>
                </div>

                <div className="p-8 flex-grow">
                    
                    {/* === PASO 1 === */}
                    {step === 1 && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right">
                            
                            {/* SELECTOR TIPO PERSONA */}
                            <div className="flex bg-gray-100 p-1 rounded-lg mb-6">
                                <button
                                    onClick={() => setFormData({...formData, tipo_persona: 'NATURAL', rif: ''})}
                                    className={`flex-1 py-2 rounded-md text-sm font-bold flex items-center justify-center gap-2 transition-all ${formData.tipo_persona === 'NATURAL' ? 'bg-white text-blue-900 shadow' : 'text-gray-500'}`}
                                >
                                    <User size={16}/> Persona Natural
                                </button>
                                <button
                                    onClick={() => setFormData({...formData, tipo_persona: 'JURIDICO', cedula: ''})}
                                    className={`flex-1 py-2 rounded-md text-sm font-bold flex items-center justify-center gap-2 transition-all ${formData.tipo_persona === 'JURIDICO' ? 'bg-white text-blue-900 shadow' : 'text-gray-500'}`}
                                >
                                    <Building2 size={16}/> Empresa
                                </button>
                            </div>

                            <h3 className="text-xl font-bold text-gray-800">Datos de Identificación</h3>
                            
                            <div>
                                <label className="block text-sm font-bold text-gray-700">
                                    {formData.tipo_persona === 'NATURAL' ? 'Nombre y Apellido' : 'Razón Social'}
                                </label>
                                <input 
                                    type="text" name="nombre_completo"
                                    value={formData.nombre_completo} onChange={handleChange}
                                    className="w-full mt-1 p-3 border border-gray-300 rounded-lg outline-none focus:border-blue-900"
                                    placeholder={formData.tipo_persona === 'NATURAL' ? "Ej. Juan Perez" : "Ej. Inversiones Whola C.A."}
                                />
                                <ErrorMsg msg={errors.nombre_completo} />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                {formData.tipo_persona === 'NATURAL' ? (
                                    <>
                                        <div>
                                            <label className="block text-sm font-bold text-gray-700">Cédula</label>
                                            <input 
                                                type="number" name="cedula"
                                                value={formData.cedula} onChange={handleChange}
                                                className="w-full mt-1 p-3 border border-gray-300 rounded-lg outline-none focus:border-blue-900"
                                                placeholder="12345678"
                                            />
                                            <ErrorMsg msg={errors.cedula} />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-bold text-gray-400">RIF (Auto)</label>
                                            <input type="text" value={formData.rif} readOnly className="w-full mt-1 p-3 bg-gray-100 border rounded-lg text-gray-500"/>
                                        </div>
                                    </>
                                ) : (
                                    <div className="col-span-2">
                                        <label className="block text-sm font-bold text-gray-700">RIF Jurídico</label>
                                        <input 
                                            type="text" name="rif"
                                            value={formData.rif} onChange={handleChange}
                                            className="w-full mt-1 p-3 border border-gray-300 rounded-lg outline-none focus:border-blue-900"
                                            placeholder="J-12345678-9"
                                        />
                                        <ErrorMsg msg={errors.rif} />
                                    </div>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700">Teléfono</label>
                                <input 
                                    type="text" name="telefono"
                                    value={formData.telefono} onChange={handleChange}
                                    className="w-full mt-1 p-3 border border-gray-300 rounded-lg outline-none focus:border-blue-900"
                                    placeholder="0414..."
                                />
                                <ErrorMsg msg={errors.telefono} />
                            </div>

                            <button onClick={() => { if(validateStep1()) setStep(2); }} className="w-full bg-blue-900 text-white font-bold py-3 rounded-lg hover:bg-blue-800 flex justify-center items-center gap-2">
                                Siguiente <ArrowRight size={18}/>
                            </button>
                        </div>
                    )}

                    {/* === PASO 2 === */}
                    {step === 2 && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right">
                            <h3 className="text-xl font-bold text-gray-800">
                                {formData.tipo_persona === 'NATURAL' ? 'Perfil Financiero' : 'Datos Comerciales'}
                            </h3>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-bold text-gray-700">
                                        {formData.tipo_persona === 'NATURAL' ? 'Fecha Nacimiento' : 'Fecha Constitución'}
                                    </label>
                                    <div className="relative">
                                        <Calendar size={18} className="absolute top-4 left-3 text-orange-600"/>
                                        <input type="date" value={formData.fecha_nacimiento} readOnly className="w-full mt-1 pl-10 p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-900 font-bold"/>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-400">
                                        {formData.tipo_persona === 'NATURAL' ? 'Estado Civil' : 'Domicilio Fiscal'}
                                    </label>
                                    <input type="text" value={formData.estado_civil || 'N/A'} readOnly className="w-full mt-1 p-3 bg-gray-100 rounded-lg text-gray-500"/>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-bold text-gray-400">
                                        {formData.tipo_persona === 'NATURAL' ? 'Profesión' : 'Actividad Económica'}
                                    </label>
                                    <input type="text" value={formData.profesion} readOnly className="w-full mt-1 p-3 bg-gray-100 rounded-lg text-gray-500"/>
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-400">Origen Fondos</label>
                                    <input type="text" value={formData.origen_fondos} readOnly className="w-full mt-1 p-3 bg-gray-100 rounded-lg text-gray-500"/>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700">Email Corporativo/Personal</label>
                                <input type="text" value={formData.email} readOnly className="w-full mt-1 p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-900 font-bold"/>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button onClick={() => setStep(1)} className="w-1/3 border border-gray-300 text-gray-600 font-bold py-3 rounded-lg hover:bg-gray-50">Atrás</button>
                                <button onClick={() => setStep(3)} className="w-2/3 bg-blue-900 text-white font-bold py-3 rounded-lg hover:bg-blue-800">Siguiente</button>
                            </div>
                        </div>
                    )}

                    {/* === PASO 3 (Igual para ambos) === */}
                    {step === 3 && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-right">
                            <h3 className="text-xl font-bold text-gray-800">Credenciales de Acceso</h3>
                            
                            <div>
                                <label className="block text-sm font-bold text-gray-700">Usuario</label>
                                <input 
                                    type="text" 
                                    value={formData.username} 
                                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                                    className="w-full mt-1 p-3 border border-gray-300 rounded-lg focus:border-blue-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700">Contraseña</label>
                                <input 
                                    type="password"
                                    value={formData.password}
                                    onChange={(e) => {
                                        setFormData({...formData, password: e.target.value});
                                        checkPasswordStrength(e.target.value);
                                    }}
                                    className="w-full mt-1 p-3 border border-gray-300 rounded-lg focus:border-blue-900"
                                    placeholder="••••••••"
                                />
                                <div className="mt-2 h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                                    <div className={`h-full transition-all duration-300 ${passwordStrength < 50 ? 'bg-red-500' : 'bg-green-500'}`} style={{ width: `${passwordStrength}%` }}></div>
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button onClick={() => setStep(2)} className="w-1/3 border border-gray-300 text-gray-600 font-bold py-3 rounded-lg hover:bg-gray-50">Atrás</button>
                                <button 
                                    onClick={handleSubmit} 
                                    disabled={passwordStrength < 50 || loading}
                                    className="w-2/3 bg-orange-600 text-white font-bold py-3 rounded-lg hover:bg-orange-700 disabled:opacity-50 shadow-lg"
                                >
                                    {loading ? 'Procesando...' : 'FINALIZAR REGISTRO'}
                                </button>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default Register;