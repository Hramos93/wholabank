// frontend/src/pages/Home.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Menu, Search, CreditCard, Smartphone, BookOpen, 
  Info, ChevronRight, User, Briefcase, Lock, ArrowRight 
} from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('personas'); 

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      
      {/* === HEADER SUPERIOR (NAVBAR) === */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            
            {/* Logo y Tabs */}
            <div className="flex items-center gap-8">
              {/* LOGO WHOLA */}
              <div className="flex items-center gap-2 cursor-pointer group" onClick={() => navigate('/')}>
                <div className="bg-blue-900 text-white font-black text-3xl px-3 py-1 rounded-tr-xl rounded-bl-xl italic shadow-lg group-hover:bg-blue-800 transition-colors">
                  W
                </div>
                <span className="text-3xl font-extrabold text-blue-900 tracking-tighter">
                  WHOLA
                </span>
              </div>

              {/* Pestañas Personas / Empresas */}
              <div className="hidden md:flex space-x-2 bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => setActiveTab('personas')}
                  className={`px-5 py-2 text-sm font-bold rounded-md transition-all ${
                    activeTab === 'personas' 
                      ? 'bg-white text-blue-900 shadow-sm' 
                      : 'text-gray-500 hover:text-blue-900'
                  }`}
                >
                  Personas
                </button>
                <button
                  onClick={() => setActiveTab('empresas')}
                  className={`px-5 py-2 text-sm font-bold rounded-md transition-all ${
                    activeTab === 'empresas' 
                      ? 'bg-white text-blue-900 shadow-sm' 
                      : 'text-gray-500 hover:text-blue-900'
                  }`}
                >
                  Empresas
                </button>
              </div>
            </div>

            {/* Buscador */}
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center bg-gray-100 px-4 py-2 rounded-full border border-gray-200 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
                <Search size={18} className="text-gray-400" />
                <input 
                    type="text" 
                    placeholder="¿Qué estás buscando?" 
                    className="bg-transparent border-none outline-none text-sm ml-2 w-48 text-gray-700 placeholder-gray-400"
                />
              </div>
              <div className="md:hidden p-2">
                <Menu size={28} className="text-blue-900" />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* === CONTENIDO PRINCIPAL === */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-grow">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* === SIDEBAR IZQUIERDO (Col 1-3) === */}
          <aside className="lg:col-span-3 space-y-6">
            
            {/* Tarjeta de Acceso Rápido */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 space-y-3">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Accesos Directos</p>
              
              {/* Botón 1: Login */}
              <button 
                onClick={() => navigate('/login')}
                className="w-full bg-blue-900 text-white px-4 py-4 rounded-lg shadow-md hover:bg-blue-800 flex items-center justify-between group transition-all active:scale-95"
              >
                <div className="flex items-center gap-3">
                    <div className="bg-blue-800 p-1.5 rounded text-blue-200">
                        <Lock size={18} />
                    </div>
                    <div className="text-left leading-tight">
                        <span className="block font-bold text-sm">Whola en Línea</span>
                        <span className="text-xs text-blue-200">Ingreso seguro</span>
                    </div>
                </div>
                <ChevronRight size={18} className="opacity-70 group-hover:translate-x-1 transition-transform" />
              </button>

              {/* Botón 2: Hazte Cliente (LINK ACTUALIZADO) */}
              <button 
                onClick={() => navigate('/register')} // <--- AQUI ESTA EL CAMBIO
                className="w-full bg-cyan-600 text-white px-4 py-4 rounded-lg shadow-md hover:bg-cyan-700 flex items-center justify-between group transition-all active:scale-95"
              >
                <div className="flex items-center gap-3">
                    <div className="bg-cyan-500 p-1.5 rounded text-white">
                        <User size={18} />
                    </div>
                    <span className="font-bold text-sm">Hazte Cliente</span>
                </div>
                <ChevronRight size={18} className="opacity-70 group-hover:translate-x-1 transition-transform" />
              </button>

              {/* Botón 3: Portal de Pagos (Datáfono) */}
              <button 
                onClick={() => navigate('/pos')}
                className="w-full bg-orange-600 text-white px-4 py-4 rounded-lg shadow-md hover:bg-orange-700 flex items-center justify-between group transition-all active:scale-95"
              >
                <div className="flex items-center gap-3">
                    <div className="bg-orange-500 p-1.5 rounded text-white">
                        <CreditCard size={18} />
                    </div>
                    <div className="text-left leading-tight">
                        <span className="block font-bold text-sm">Portal de Pagos</span>
                        <span className="text-xs text-orange-100">Puntos de Venta</span>
                    </div>
                </div>
                <ChevronRight size={18} className="opacity-70 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>

            {/* Menú de Navegación Lateral */}
            <nav className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <NavItem icon={<CreditCard size={20}/>} text="Productos" />
                <div className="h-px bg-gray-100 mx-4"></div>
                <NavItem icon={<Smartphone size={20}/>} text="Servicios Digitales" />
                <div className="h-px bg-gray-100 mx-4"></div>
                <NavItem icon={<BookOpen size={20}/>} text="Conoce Whola" />
                <div className="h-px bg-gray-100 mx-4"></div>
                <NavItem icon={<Info size={20}/>} text="Información y Ayuda" />
            </nav>
          </aside>

          {/* === HERO SECTION CENTRAL (Col 4-12) === */}
          <main className="lg:col-span-9 space-y-8">
            
            {/* Banner Principal */}
            <div className="bg-blue-900 rounded-2xl shadow-xl overflow-hidden text-white relative min-h-[400px] flex flex-col md:flex-row">
              
              {/* Contenido Texto */}
              <div className="p-8 md:p-12 md:w-3/5 z-10 flex flex-col justify-center">
                <div className="inline-block bg-orange-500 text-white text-xs font-bold px-3 py-1 rounded-full w-fit mb-4">
                  NUEVA APERTURA DIGITAL
                </div>
                
                <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
                  Tu cuenta bancaria <br/>
                  <span className="text-cyan-400">al alcance de un clic.</span>
                </h1>
                
                <p className="text-blue-100 text-lg mb-8 max-w-md">
                  Sin ir a la agencia. Abre tu Cuenta Corriente solo con tu cédula y empieza a mover tu dinero hoy mismo.
                </p>

                <div className="flex flex-wrap gap-4">
                  {/* Botón Principal Banner (LINK ACTUALIZADO) */}
                  <button 
                    onClick={() => navigate('/register')} // <--- AQUI ESTA EL CAMBIO
                    className="bg-white text-blue-900 font-bold py-3 px-8 rounded-full shadow hover:bg-gray-100 transition-colors active:scale-95 flex items-center gap-2"
                  >
                    Abrir mi cuenta
                    <ArrowRight size={18} />
                  </button>
                  
                  <button className="bg-transparent border-2 border-cyan-400 text-cyan-400 font-bold py-3 px-6 rounded-full hover:bg-blue-800 transition-colors active:scale-95">
                    Más información
                  </button>
                </div>
              </div>

              {/* Imagen de Fondo / Decorativa */}
              <div className="md:w-2/5 relative h-64 md:h-auto bg-blue-800">
                 <div className="absolute top-10 right-10 w-32 h-32 bg-cyan-500 rounded-full blur-3xl opacity-30"></div>
                 <div className="absolute bottom-10 left-10 w-40 h-40 bg-orange-500 rounded-full blur-3xl opacity-20"></div>
                 
                 <div 
                    className="absolute inset-0 bg-cover bg-center mix-blend-luminosity opacity-80"
                    style={{ backgroundImage: "url('https://images.unsplash.com/photo-1573164713988-8665fc963095?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80')" }}
                 ></div>
                 <div className="absolute inset-0 bg-gradient-to-r from-blue-900 via-blue-900/40 to-transparent"></div>
              </div>
            </div>

            {/* Banners Secundarios */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer group">
                    <div className="flex justify-between items-start mb-4">
                        <div className="bg-orange-100 p-3 rounded-full text-orange-600">
                            <Briefcase size={24} />
                        </div>
                        <ChevronRight className="text-gray-300 group-hover:text-orange-500 transition-colors" />
                    </div>
                    <h3 className="font-bold text-xl text-gray-800 mb-2">Crédito Personal</h3>
                    <p className="text-gray-500 text-sm">Calcula tus cuotas y solicita tu crédito sin inicial.</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer group">
                    <div className="flex justify-between items-start mb-4">
                        <div className="bg-blue-100 p-3 rounded-full text-blue-900">
                            <Lock size={24} />
                        </div>
                        <ChevronRight className="text-gray-300 group-hover:text-blue-900 transition-colors" />
                    </div>
                    <h3 className="font-bold text-xl text-gray-800 mb-2">Seguridad Whola</h3>
                    <p className="text-gray-500 text-sm">Conoce cómo protegemos tus transacciones digitales.</p>
                </div>
            </div>

          </main>
        </div>
      </div>
    </div>
  );
};

const NavItem = ({ icon, text }) => (
    <div className="flex items-center gap-4 px-5 py-4 text-gray-600 hover:text-blue-900 hover:bg-blue-50 cursor-pointer transition-colors group">
        <span className="text-gray-400 group-hover:text-blue-900 transition-colors">{icon}</span>
        <span className="font-semibold text-sm">{text}</span>
        <ChevronRight size={16} className="ml-auto opacity-0 group-hover:opacity-100 text-blue-900 transition-all transform -translate-x-2 group-hover:translate-x-0" />
    </div>
);

export default Home;