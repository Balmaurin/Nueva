'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

// ===== DASHBOARD CON PESTAÑAS SUPERIORES =====
// Diseño tradicional con navegación por pestañas

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading } = useAuth();
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState('general');
  const [currentSection, setCurrentSection] = useState('overview');
  const [phantomWallet, setPhantomWallet] = useState({
    connected: false,
    address: '',
    balance: 0
  });
  const [tokenBalance, setTokenBalance] = useState(150);
  const chatMessagesRef = useRef(null);

  // Datos simulados para el dashboard
  const branches = [
    { id: '1', name: 'Machine Learning', description: 'Aprendizaje automático avanzado', keywords: ['ML', 'AI', 'Algoritmos'] },
    { id: '2', name: 'Natural Language Processing', description: 'Procesamiento de lenguaje natural', keywords: ['NLP', 'Texto', 'Lenguaje'] },
    { id: '3', name: 'Computer Vision', description: 'Visión por computadora', keywords: ['CV', 'Imágenes', 'Visión'] }
  ];

  // Funciones del chat
  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const message = chatInput.trim();
    setChatInput('');
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:8005/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [{
            role: "user",
            content: message
          }],
          max_tokens: 300,
          temperature: 0.7
        })
      });

      if (response.ok) {
        const data = await response.json();
        setChatMessages(prev => [...prev, {
          id: Date.now(),
          text: message,
          sender: 'user',
          timestamp: new Date()
        }, {
          id: Date.now() + 1,
          text: data.response,
          sender: 'sheily',
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Error en chat:', error);
      setChatMessages(prev => [...prev, {
        id: Date.now(),
        text: 'Error conectando con Sheily AI',
        sender: 'system',
        timestamp: new Date()
      }]);
    }
    setIsChatLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  // Funciones de wallet
  const connectPhantom = () => {
    setPhantomWallet({
      connected: true,
      address: 'ABC123...XYZ789',
      balance: 150.75
    });
  };

  const disconnectPhantom = () => {
    setPhantomWallet({
      connected: false,
      address: '',
      balance: 0
    });
  };

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* Header Superior con Pestañas */}
      <header className="bg-gray-800 border-b border-gray-700 flex-shrink-0">
        {/* Título */}
        <div className="px-6 py-4 flex items-center justify-between border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🚀</span>
            <div>
              <h1 className="text-xl font-bold text-blue-400">Sheily AI</h1>
              <p className="text-xs text-gray-400">Sistema de Inteligencia Artificial Avanzado</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-xs text-gray-400">Usuario</p>
              <p className="text-sm font-medium">{user?.username || 'Usuario'}</p>
            </div>
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-sm">👤</span>
            </div>
          </div>
        </div>

        {/* Pestañas */}
        <nav className="px-6 py-2">
          <div className="flex space-x-1 overflow-x-auto">
            {[
              { id: 'overview', label: '📊 Sistema', desc: 'Métricas en tiempo real' },
              { id: 'chat', label: '💬 Chat con Sheily', desc: 'Conecta a Llama 3.2 Q4' },
              { id: 'wallet', label: '👻 Phantom Wallet', desc: 'Conectar/desconectar' },
              { id: 'tokens', label: '🪙 Tokens SHEILY', desc: 'Balance, transacciones' },
              { id: 'training', label: '🎓 Entrenamiento', desc: 'Ejercicios, progreso' },
              { id: 'branches', label: '🌿 35 Ramas IA', desc: 'Exploración completa' },
              { id: 'governance', label: '🏛️ Gobernanza', desc: 'Votaciones DAO' },
              { id: 'analytics', label: '📈 Analytics', desc: 'Rendimiento IA' },
              { id: 'settings', label: '⚙️ Configuración', desc: 'Ajustes completos' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setCurrentSection(tab.id)}
                className={`flex-shrink-0 px-4 py-2 rounded-lg text-xs font-medium transition-colors ${
                  currentSection === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                <div className="text-center">
                  <div>{tab.label}</div>
                  <div className="text-xs opacity-75">{tab.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </nav>
      </header>

      {/* Contenido Principal */}
      <main className="flex-1 overflow-auto p-6">
        {currentSection === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-600 rounded-lg">
                    <span className="text-xl">💻</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">CPU</p>
                    <p className="text-2xl font-bold">45%</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <span className="text-xl">🧠</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Memoria</p>
                    <p className="text-2xl font-bold">67%</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-600 rounded-lg">
                    <span className="text-xl">💾</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Disco</p>
                    <p className="text-2xl font-bold">23%</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-600 rounded-lg">
                    <span className="text-xl">🌐</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Conexiones</p>
                    <p className="text-2xl font-bold">1,247</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Estado de Servicios</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Llama 3.2 Q4 Server</span>
                    <span className="text-green-400">● Online</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>API Backend</span>
                    <span className="text-green-400">● Online</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Base de Datos</span>
                    <span className="text-green-400">● Online</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Blockchain Node</span>
                    <span className="text-yellow-400">● Syncing</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Notificaciones Recientes</h3>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <span className="text-blue-400">ℹ️</span>
                    <div>
                      <p className="text-sm">Nuevo ejercicio disponible</p>
                      <p className="text-xs text-gray-400">Hace 2 minutos</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-green-400">✅</span>
                    <div>
                      <p className="text-sm">Tokens SHEILY reclamados</p>
                      <p className="text-xs text-gray-400">Hace 15 minutos</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-yellow-400">⚠️</span>
                    <div>
                      <p className="text-sm">Mantenimiento programado</p>
                      <p className="text-xs text-gray-400">En 2 horas</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentSection === 'chat' && (
          <div className="h-full flex flex-col">
            {/* Selector de rama */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Rama especializada:</label>
              <select
                value={selectedBranch}
                onChange={(e) => setSelectedBranch(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 w-full max-w-md"
              >
                {branches.map(branch => (
                  <option key={branch.id} value={branch.name}>
                    {branch.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>

            {/* Mensajes */}
            <div
              ref={chatMessagesRef}
              className="flex-1 bg-gray-800 rounded-lg p-4 overflow-y-auto mb-4 min-h-96"
            >
              {chatMessages.length === 0 ? (
                <div className="text-center text-gray-400 mt-8">
                  <p className="text-lg mb-2">¡Hola! Soy Sheily AI 🤖</p>
                  <p>Pregúntame cualquier cosa sobre las 35 ramas especializadas de IA</p>
                </div>
              ) : (
                chatMessages.map(msg => (
                  <div key={msg.id} className={`mb-4 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block p-4 rounded-lg max-w-2xl ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : msg.sender === 'sheily'
                          ? 'bg-gray-700 text-gray-100'
                          : 'bg-red-600 text-white'
                    }`}>
                      <p className="text-sm">{msg.text}</p>
                      <p className="text-xs opacity-75 mt-2">{msg.timestamp.toLocaleTimeString()}</p>
                    </div>
                  </div>
                ))
              )}
              {isChatLoading && (
                <div className="text-center text-gray-400 mt-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 inline-block"></div>
                  <p className="mt-2">Sheily está pensando...</p>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Pregunta a Sheily..."
                className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={sendChatMessage}
                disabled={isChatLoading}
                className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium disabled:opacity-50"
              >
                📤 Enviar
              </button>
            </div>
          </div>
        )}

        {currentSection === 'wallet' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Phantom Wallet Integration</h2>
                <p className="text-gray-400">Conecta tu wallet y gestiona tokens SHEILY en Solana</p>
              </div>
            </div>

            {phantomWallet.connected ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Wallet Conectada</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-400">Dirección</p>
                      <p className="font-mono text-sm bg-gray-700 p-2 rounded">{phantomWallet.address}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-400">Balance</p>
                      <p className="text-2xl font-bold text-green-400">{phantomWallet.balance} SOL</p>
                    </div>
                  </div>
                  <button
                    onClick={disconnectPhantom}
                    className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium mt-4"
                  >
                    🔌 Desconectar Wallet
                  </button>
                </div>

                <div className="bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Transacciones Recientes</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
                      <div>
                        <p className="text-sm">Compra tokens SHEILY</p>
                        <p className="text-xs text-gray-400">Hace 2 horas</p>
                      </div>
                      <span className="text-green-400">+50 SHEILY</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
                      <div>
                        <p className="text-sm">Stake DAO</p>
                        <p className="text-xs text-gray-400">Hace 1 día</p>
                      </div>
                      <span className="text-red-400">-25 SHEILY</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-4xl">👻</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Conecta tu Phantom Wallet</h3>
                <p className="text-gray-400 mb-6">Accede a todas las funciones blockchain de Sheily AI</p>
                <button
                  onClick={connectPhantom}
                  className="bg-purple-600 hover:bg-purple-700 px-8 py-3 rounded-lg font-medium"
                >
                  🔗 Conectar Phantom
                </button>
              </div>
            )}
          </div>
        )}

        {currentSection === 'tokens' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Sistema de Tokens SHEILY</h2>
                <p className="text-gray-400">Economía completa en blockchain Solana</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="text-center">
                  <p className="text-6xl font-bold text-yellow-400 mb-2">{tokenBalance.toLocaleString()}</p>
                  <p className="text-gray-400">Tokens SHEILY disponibles</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Ganancias Recientes</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Ejercicio completado</span>
                    <span className="text-green-400">+50 SHEILY</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Chat premium</span>
                    <span className="text-green-400">+25 SHEILY</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Contribución comunidad</span>
                    <span className="text-green-400">+10 SHEILY</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Gastos Recientes</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Stake DAO</span>
                    <span className="text-red-400">-10 SHEILY</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Compra NFT</span>
                    <span className="text-red-400">-5 SHEILY</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentSection === 'training' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Sistema de Entrenamiento Interactivo</h2>
                <p className="text-gray-400">Completa ejercicios en diferentes ramas para ganar tokens SHEILY</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Ejercicio Actual</h3>
                <div className="space-y-4">
                  <div>
                    <p className="font-semibold text-lg">Machine Learning Básico</p>
                    <p className="text-gray-400">Aprende los fundamentos del aprendizaje automático</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Progreso</p>
                    <div className="w-full bg-gray-700 rounded-full h-3">
                      <div className="bg-pink-500 h-3 rounded-full" style={{width: '75%'}}></div>
                    </div>
                    <p className="text-sm mt-1">75% completado</p>
                  </div>
                  <div className="flex space-x-2">
                    <button className="flex-1 bg-pink-600 hover:bg-pink-700 px-4 py-2 rounded-lg font-medium">
                      Continuar Ejercicio
                    </button>
                    <button className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-medium">
                      Nuevo Ejercicio
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Historial de Ejercicios</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
                    <div>
                      <p className="font-medium">Python Fundamentals</p>
                      <p className="text-sm text-gray-400">Completado - Hace 2 días</p>
                    </div>
                    <span className="text-green-400">+30 SHEILY</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-700 rounded">
                    <div>
                      <p className="font-medium">Data Science Basics</p>
                      <p className="text-sm text-gray-400">Completado - Hace 5 días</p>
                    </div>
                    <span className="text-green-400">+45 SHEILY</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentSection === 'branches' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">35 Ramas Especializadas de IA</h2>
                <p className="text-gray-400">Explora todas las especializaciones disponibles</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {branches.map(branch => (
                <div key={branch.id} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors">
                  <div className="flex items-center mb-3">
                    <span className="text-2xl mr-3">🌿</span>
                    <div>
                      <h3 className="font-semibold text-cyan-400">{branch.name}</h3>
                      <p className="text-sm text-gray-400">{branch.description}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-4">
                    {branch.keywords.map((keyword, idx) => (
                      <span key={idx} className="bg-cyan-600 text-xs px-2 py-1 rounded-full">
                        {keyword}
                      </span>
                    ))}
                  </div>
                  <button className="w-full bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-lg font-medium">
                    Explorar Rama
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentSection === 'governance' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Gobernanza DAO</h2>
                <p className="text-gray-400">Participa en la gobernanza con tus tokens SHEILY</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Propuestas Activas</h3>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-700 rounded">
                    <h4 className="font-semibold mb-2">Nueva Rama IA: Quantum Computing</h4>
                    <p className="text-sm text-gray-400 mb-3">Implementar soporte para computación cuántica en el sistema</p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Votos: 234/500</span>
                      <button className="bg-orange-600 hover:bg-orange-700 px-4 py-1 rounded text-sm">
                        Votar Sí
                      </button>
                    </div>
                  </div>

                  <div className="p-4 bg-gray-700 rounded">
                    <h4 className="font-semibold mb-2">Aumento de Tokens Diarios</h4>
                    <p className="text-sm text-gray-400 mb-3">Incrementar la recompensa diaria de 10 a 15 tokens</p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Votos: 189/500</span>
                      <button className="bg-orange-600 hover:bg-orange-700 px-4 py-1 rounded text-sm">
                        Votar Sí
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Tu Participación</h3>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-orange-400">1,250</p>
                    <p className="text-gray-400">Votos disponibles</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Poder de voto</p>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className="bg-orange-500 h-2 rounded-full" style={{width: '75%'}}></div>
                    </div>
                    <p className="text-xs mt-1">75% basado en stake</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentSection === 'analytics' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Analytics y Estadísticas</h2>
                <p className="text-gray-400">Análisis detallado del rendimiento del sistema</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-400">47</p>
                  <p className="text-gray-400">Chats de hoy</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-400">12</p>
                  <p className="text-gray-400">Ejercicios completados</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-400">89%</p>
                  <p className="text-gray-400">Precisión IA</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-yellow-400">1.2s</p>
                  <p className="text-gray-400">Tiempo respuesta promedio</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Uso por Rama IA</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Machine Learning</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-700 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{width: '85%'}}></div>
                      </div>
                      <span className="text-sm">85%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>NLP</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-700 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{width: '72%'}}></div>
                      </div>
                      <span className="text-sm">72%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Computer Vision</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-700 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{width: '68%'}}></div>
                      </div>
                      <span className="text-sm">68%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Rendimiento del Sistema</h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-400 mb-1">CPU Usage (24h)</p>
                    <div className="w-full bg-gray-700 rounded-full h-3">
                      <div className="bg-red-500 h-3 rounded-full" style={{width: '45%'}}></div>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Memory Usage (24h)</p>
                    <div className="w-full bg-gray-700 rounded-full h-3">
                      <div className="bg-blue-500 h-3 rounded-full" style={{width: '67%'}}></div>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Disk Usage (24h)</p>
                    <div className="w-full bg-gray-700 rounded-full h-3">
                      <div className="bg-yellow-500 h-3 rounded-full" style={{width: '23%'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentSection === 'settings' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Configuración del Sistema</h2>
                <p className="text-gray-400">Personaliza tu experiencia en Sheily AI</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Tema</h3>
                <div className="space-y-3">
                  <button className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium">
                    Tema Oscuro
                  </button>
                  <button className="w-full bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-medium">
                    Tema Claro
                  </button>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Idioma</h3>
                <div className="space-y-3">
                  <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                    <option>Español</option>
                    <option>English</option>
                    <option>Français</option>
                    <option>Deutsch</option>
                  </select>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Notificaciones</h3>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm">Ejercicios completados</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm">Nuevos tokens</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">Propuestas DAO</span>
                  </label>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Privacidad</h3>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm">Guardar historial de chat</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">Analytics anónimos</span>
                  </label>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Cuenta</h3>
                <div className="space-y-3">
                  <button className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium">
                    Cambiar Contraseña
                  </button>
                  <button className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium">
                    Cerrar Sesión
                  </button>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Avanzado</h3>
                <div className="space-y-3">
                  <button className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium">
                    Exportar Datos
                  </button>
                  <button className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium">
                    Eliminar Cuenta
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
