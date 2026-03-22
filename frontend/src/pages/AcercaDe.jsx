import React from 'react';
import { Building2, Target, Lightbulb, ShieldCheck, Globe, TrendingUp } from 'lucide-react';

export default function AcercaDe() {
  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-800">
      {/* Hero Section */}
      <div className="bg-blue-900 text-white py-20 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-6 tracking-tight">
            Acerca de WholaBank
          </h1>
          <p className="text-lg md:text-xl text-blue-100 max-w-3xl mx-auto leading-relaxed">
            Redefiniendo las fronteras de la banca digital a través de la innovación, 
            la seguridad y la interoperabilidad sin límites.
          </p>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-6xl mx-auto px-6 py-16 space-y-20">
        
        {/* Historia */}
        <section className="flex flex-col md:flex-row items-center gap-12">
          <div className="w-full md:w-1/2 flex justify-center">
            <div className="bg-blue-100 p-8 rounded-full shadow-inner">
              <Building2 size={120} className="text-blue-700" />
            </div>
          </div>
          <div className="w-full md:w-1/2">
            <h2 className="text-3xl font-bold text-blue-900 mb-6">Nuestra Historia</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              WholaBank nace como una iniciativa vanguardista diseñada para romper los silos 
              tradicionales del ecosistema financiero. Surgimos con la firme convicción de que 
              los sistemas bancarios no deben ser islas aisladas, sino ecosistemas conectados.
            </p>
            <p className="text-gray-600 leading-relaxed">
              Desde el primer día, nuestro núcleo bancario (Core) fue construido desde cero con 
              una arquitectura orientada a APIs (API-First), preparándonos para hablar el lenguaje 
              del futuro: la interoperabilidad B2B y el Open Banking, facilitando pagos y 
              transferencias con cualquier entidad aliada en milisegundos.
            </p>
          </div>
        </section>

        {/* Misión y Visión */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {/* Misión Card */}
          <div className="bg-white rounded-2xl shadow-lg p-10 border-t-4 border-blue-600 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center gap-4 mb-6">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Target className="text-blue-700" size={32} />
              </div>
              <h2 className="text-2xl font-bold text-blue-900">Misión</h2>
            </div>
            <p className="text-gray-600 leading-relaxed">
              Proveer una infraestructura financiera robusta, segura y altamente interoperable 
              que facilite las operaciones entre comercios, usuarios y bancos aliados. Nos 
              esforzamos por democratizar las finanzas ofreciendo un núcleo transaccional 
              que garantice pagos fluidos, atómicos y confiables en tiempo real.
            </p>
          </div>

          {/* Visión Card */}
          <div className="bg-white rounded-2xl shadow-lg p-10 border-t-4 border-teal-500 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-center gap-4 mb-6">
              <div className="bg-teal-100 p-3 rounded-lg">
                <Lightbulb className="text-teal-700" size={32} />
              </div>
              <h2 className="text-2xl font-bold text-blue-900">Visión</h2>
            </div>
            <p className="text-gray-600 leading-relaxed">
              Convertirnos en el referente tecnológico líder en la nueva era del Open Banking 
              a nivel regional. Aspiramos a ser la plataforma base que establezca el estándar 
              para las integraciones de APIs financieras, impulsando el crecimiento de la 
              economía digital sin barreras.
            </p>
          </div>
        </section>

        {/* Valores */}
        <section>
          <h2 className="text-3xl font-bold text-center text-blue-900 mb-12">Nuestros Valores</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
              <Globe className="mx-auto text-blue-500 mb-4" size={48} />
              <h3 className="text-xl font-bold text-gray-800 mb-3">Interoperabilidad</h3>
              <p className="text-gray-600 text-sm">
                Diseñados para conectar. Hablamos el lenguaje universal de los sistemas financieros 
                para enrutar operaciones sin fricción.
              </p>
            </div>
            
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
              <ShieldCheck className="mx-auto text-blue-500 mb-4" size={48} />
              <h3 className="text-xl font-bold text-gray-800 mb-3">Seguridad Atómica</h3>
              <p className="text-gray-600 text-sm">
                Protegemos cada transacción. Nuestra arquitectura garantiza consistencia de datos 
                y auditoría estricta en cada movimiento.
              </p>
            </div>
            
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
              <TrendingUp className="mx-auto text-blue-500 mb-4" size={48} />
              <h3 className="text-xl font-bold text-gray-800 mb-3">Innovación Continua</h3>
              <p className="text-gray-600 text-sm">
                La tecnología es nuestro motor. Evolucionamos constantemente para ofrecer soluciones 
                bancarias de última generación.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}