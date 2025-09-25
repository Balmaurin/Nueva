'use client';

import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useRouter } from 'next/navigation';

function LandingPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      let result;
      if (isLogin) {
        result = await login(formData.username, formData.password);
      } else {
        result = await register(formData.username, formData.email, formData.password);
      }

      setMessage(result.message);

      if (result.success) {
        if (isLogin) {
          // Redirigir al dashboard después del login
          router.push('/dashboard');
        } else {
          // Cambiar a login después del registro
          setIsLogin(true);
          setFormData({ username: '', email: '', password: '' });
        }
      }
    } catch (error) {
      setMessage('Error de conexión. Verifica que el servidor esté funcionando.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-500/10 rounded-full blur-2xl animate-bounce"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 px-6 py-4 backdrop-blur-sm">
        <nav className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-xl flex items-center justify-center shadow-lg hover:shadow-cyan-500/25 transition-shadow duration-300">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <span className="text-white font-bold text-2xl bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Sheily AI
            </span>
          </div>
          <div className="hidden md:flex space-x-8">
            <a href="#features" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 relative group">
              Características
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-cyan-400 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="#about" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 relative group">
              Acerca de
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-cyan-400 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="#contact" className="text-gray-300 hover:text-white transition-all duration-300 hover:scale-105 relative group">
              Contacto
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-cyan-400 group-hover:w-full transition-all duration-300"></span>
            </a>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative px-6 py-20">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <div className="space-y-8 animate-fade-in">
            <div className="space-y-4">
              <h1 className="text-5xl lg:text-7xl font-bold text-white leading-tight animate-slide-up">
                Inteligencia Artificial
                <span className="block bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent animate-gradient">
                  Especializada
                </span>
              </h1>
              <p className="text-xl text-gray-300 leading-relaxed animate-slide-up delay-200">
                Descubre el poder de la IA con nuestro sistema avanzado que domina <strong className="text-cyan-400">35 ramas especializadas</strong> de conocimiento.
                Desde matemáticas hasta medicina, tenemos la especialización perfecta para ti.
              </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 py-8 animate-slide-up delay-300">
              <div className="text-center group">
                <div className="text-4xl font-bold text-cyan-400 mb-2 group-hover:scale-110 transition-transform duration-300">35</div>
                <div className="text-sm text-gray-400">Ramas Especializadas</div>
                <div className="w-16 h-1 bg-cyan-400 mx-auto mt-2 rounded-full group-hover:w-24 transition-all duration-300"></div>
              </div>
              <div className="text-center group">
                <div className="text-4xl font-bold text-blue-400 mb-2 group-hover:scale-110 transition-transform duration-300">3B</div>
                <div className="text-sm text-gray-400">Parámetros</div>
                <div className="w-16 h-1 bg-blue-400 mx-auto mt-2 rounded-full group-hover:w-24 transition-all duration-300"></div>
              </div>
              <div className="text-center group">
                <div className="text-4xl font-bold text-purple-400 mb-2 group-hover:scale-110 transition-transform duration-300">99.9%</div>
                <div className="text-sm text-gray-400">Uptime</div>
                <div className="w-16 h-1 bg-purple-400 mx-auto mt-2 rounded-full group-hover:w-24 transition-all duration-300"></div>
              </div>
            </div>

            {/* CTA Button */}
            <div className="animate-slide-up delay-500">
              <Button className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold py-4 px-8 rounded-xl text-lg shadow-2xl hover:shadow-cyan-500/25 transform hover:scale-105 transition-all duration-300 glow-effect">
                🚀 Comenzar Ahora
              </Button>
            </div>
          </div>

          {/* Right Column - Login/Register Form */}
          <div className="relative animate-fade-in delay-700">
            <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/20 hover:border-cyan-400/50 transition-all duration-500 transform hover:scale-105">
              {/* Floating Orbs */}
              <div className="absolute -top-4 -right-4 w-8 h-8 bg-cyan-400/30 rounded-full blur-sm animate-pulse"></div>
              <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-purple-400/30 rounded-full blur-sm animate-pulse delay-500"></div>

              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl mb-4 shadow-lg">
                  <span className="text-2xl">🤖</span>
                </div>
                <h2 className="text-3xl font-bold text-white mb-2">
                  {isLogin ? 'Bienvenido' : 'Únete a Sheily'}
                </h2>
                <p className="text-gray-400">
                  {isLogin ? 'Accede a tu cuenta de IA especializada' : 'Crea tu cuenta y comienza tu viaje con IA'}
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-200">
                    👤 Usuario
                  </label>
                  <Input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    className="w-full bg-white/5 border-white/20 text-white placeholder-gray-400 hover:bg-white/10 focus:bg-white/10 transition-all duration-300"
                    placeholder="Tu nombre de usuario"
                  />
                </div>

                {!isLogin && (
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-200">
                      📧 Email
                    </label>
                    <Input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full bg-white/5 border-white/20 text-white placeholder-gray-400 hover:bg-white/10 focus:bg-white/10 transition-all duration-300"
                      placeholder="tu@email.com"
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-200">
                    🔒 Contraseña
                  </label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      className="w-full bg-white/5 border-white/20 text-white placeholder-gray-400 hover:bg-white/10 focus:bg-white/10 transition-all duration-300 pr-12"
                      placeholder="Tu contraseña segura"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                    >
                      {showPassword ? '🙈' : '👁️'}
                    </button>
                  </div>
                </div>

                {message && (
                  <div className={`p-4 rounded-xl text-sm font-medium animate-fade-in ${
                    message.includes('Error') || message.includes('inválidas') || message.includes('falló')
                      ? 'bg-red-500/20 border border-red-500/50 text-red-300'
                      : 'bg-green-500/20 border border-green-500/50 text-green-300'
                  }`}>
                    <div className="flex items-center space-x-2">
                      <span>{message.includes('Error') || message.includes('inválidas') ? '❌' : '✅'}</span>
                      <span>{message}</span>
                    </div>
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold py-4 text-lg rounded-xl shadow-xl hover:shadow-cyan-500/25 transform hover:scale-105 transition-all duration-300 glow-effect"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-3">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Procesando...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <span>{isLogin ? '🚀' : '✨'}</span>
                      <span>{isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}</span>
                    </div>
                  )}
                </Button>
              </form>

              <div className="mt-8 text-center">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-600"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-slate-900 text-gray-400">O</span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setIsLogin(!isLogin);
                    setMessage('');
                    setFormData({ username: '', email: '', password: '' });
                  }}
                  className="mt-4 text-cyan-400 hover:text-cyan-300 transition-all duration-300 hover:scale-105 font-medium"
                >
                  {isLogin ? '¿Nuevo aquí? Crea tu cuenta' : '¿Ya tienes cuenta? Inicia sesión'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-6 py-20 bg-black/20 relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}></div>
        </div>

        <div className="max-w-7xl mx-auto relative">
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl mb-6 shadow-lg">
              <span className="text-3xl">🚀</span>
            </div>
            <h2 className="text-5xl font-bold text-white mb-4">
              Características
              <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Revolucionarias
              </span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
              Tecnología de vanguardia con especializaciones profundas en múltiples dominios.
              Cada característica está diseñada para maximizar tu experiencia con IA.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: '🧠',
                title: 'IA Especializada',
                description: 'Modelos fine-tuned para 35 ramas específicas de conocimiento humano con precisión excepcional.',
                color: 'from-purple-500 to-pink-500'
              },
              {
                icon: '⚡',
                title: 'Alto Rendimiento',
                description: 'Procesamiento ultrarrápido con optimizaciones avanzadas de LoRA y cuantización Q4_K_M.',
                color: 'from-yellow-500 to-orange-500'
              },
              {
                icon: '🔒',
                title: 'Seguridad Total',
                description: 'Encriptación de extremo a extremo, autenticación JWT y permisos granulares.',
                color: 'from-green-500 to-teal-500'
              },
              {
                icon: '📊',
                title: 'Analytics Avanzado',
                description: 'Métricas detalladas, dashboards en tiempo real y reportes de rendimiento.',
                color: 'from-blue-500 to-cyan-500'
              },
              {
                icon: '🔄',
                title: 'Aprendizaje Continuo',
                description: 'El sistema mejora automáticamente con cada interacción y feedback del usuario.',
                color: 'from-red-500 to-pink-500'
              },
              {
                icon: '🌐',
                title: 'Multi-dominio',
                description: 'Desde matemáticas hasta medicina, dominamos todos los campos del conocimiento.',
                color: 'from-indigo-500 to-purple-500'
              }
            ].map((feature, index) => (
              <div
                key={index}
                className="group bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 hover:border-white/30 transition-all duration-500 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/10"
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl mb-6 shadow-lg group-hover:shadow-xl transition-all duration-300`}>
                  <span className="text-2xl">{feature.icon}</span>
                </div>
                <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors duration-300">
                  {feature.title}
                </h3>
                <p className="text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors duration-300">
                  {feature.description}
                </p>
                <div className="mt-4 w-0 group-hover:w-full h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 transition-all duration-500 rounded-full"></div>
              </div>
            ))}
          </div>

          {/* Call to Action */}
          <div className="text-center mt-16">
            <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-3xl p-8 border border-cyan-500/30 backdrop-blur-sm">
              <h3 className="text-3xl font-bold text-white mb-4">
                ¿Listo para experimentar la IA del futuro?
              </h3>
              <p className="text-gray-300 mb-6 text-lg">
                Únete a miles de usuarios que ya confían en Sheily AI para sus necesidades de inteligencia artificial especializada.
              </p>
              <Button className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold py-4 px-10 rounded-2xl text-lg shadow-2xl hover:shadow-cyan-500/25 transform hover:scale-105 transition-all duration-300 glow-effect">
                🚀 Comenzar Experiencia Premium
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t border-white/10 bg-black/30">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-6 h-6 bg-gradient-to-r from-cyan-400 to-blue-500 rounded flex items-center justify-center">
              <span className="text-white font-bold text-xs">S</span>
            </div>
            <span className="text-white font-bold">Sheily AI</span>
          </div>
          <p className="text-gray-400">
            © 2025 Sheily AI. Todos los derechos reservados.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default function HomePage() {
  return (
    <AuthProvider>
      <LandingPage />
    </AuthProvider>
  );
}