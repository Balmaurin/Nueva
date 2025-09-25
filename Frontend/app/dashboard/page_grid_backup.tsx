'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

// ===== SHEILY AI COMMAND CENTER =====
// DASHBOARD COMPLETO - TODAS LAS FUNCIONES EN UNA SOLA PANTALLA SIN SCROLL

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading } = useAuth();
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState('general');
  const [phantomWallet, setPhantomWallet] = useState({
    connected: false,
    address: '',
    balance: 0
  });
  const [tokenBalance, setTokenBalance] = useState(150);
  const [currentSection, setCurrentSection] = useState('overview');
  const chatMessagesRef = useRef(null);

  // Datos simulados para el dashboard
  const branches = [
    { id: '1', name: 'Machine Learning', description: 'Aprendizaje automático avanzado', keywords: ['ML', 'AI', 'Algoritmos'] },
    { id: '2', name: 'Natural Language Processing', description: 'Procesamiento de lenguaje natural', keywords: ['NLP', 'Texto', 'Lenguaje'] },
    { id: '3', name: 'Computer Vision', description: 'Visión por computadora', keywords: ['CV', 'Imágenes', 'Visión'] }
  ];

  const systemMetrics = {
    cpu: 45,
    memory: 67,
    disk: 23,
    connections: 1247
  };

  const notifications = [
    { id: 1, message: 'Nuevo ejercicio disponible', type: 'info' },
    { id: 2, message: 'Tokens SHEILY reclamados', type: 'success' }
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
    <div className="h-screen bg-gray-900 text-white overflow-hidden flex flex-col">
      {/* Header Superior - Compacto */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">🚀</span>
          <div>
            <h1 className="text-lg font-bold text-blue-400">Sheily AI - Centro de Control</h1>
            <p className="text-xs text-gray-400">Todas las funciones en una sola pantalla</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-right">
            <p className="text-xs text-gray-400">Usuario</p>
            <p className="text-sm font-medium">{user?.username || 'Usuario'}</p>
          </div>
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-sm">👤</span>
          </div>
        </div>
      </header>

      {/* Dashboard Principal - Grid sin scroll */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full grid grid-cols-12 grid-rows-4 gap-1 p-2">
          {/* Fila 1 - Chat Principal (ocupa toda la fila) */}
          <div className="col-span-9 row-span-3 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-blue-400 mb-1">💬 Chat con Sheily AI</h3>
            </div>
            <div className="flex-1 overflow-hidden">
              {/* Mensajes */}
              <div
                ref={chatMessagesRef}
                className="flex-1 bg-gray-900 rounded p-2 overflow-y-auto mb-2 text-xs"
                style={{maxHeight: '200px'}}
              >
                {chatMessages.length === 0 ? (
                  <div className="text-center text-gray-400 mt-4">
                    <p>¡Hola! Soy Sheily AI 🤖</p>
                    <p className="text-xs mt-1">Pregúntame cualquier cosa</p>
                  </div>
                ) : (
                  chatMessages.map(msg => (
                    <div key={msg.id} className={`mb-2 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                      <div className={`inline-block p-2 rounded-lg max-w-xs ${
                        msg.sender === 'user'
                          ? 'bg-blue-600 text-white'
                          : msg.sender === 'sheily'
                            ? 'bg-gray-700 text-gray-100'
                            : 'bg-red-600 text-white'
                      }`}>
                        <p className="text-xs">{msg.text}</p>
                      </div>
                    </div>
                  ))
                )}
                {isChatLoading && (
                  <div className="text-center text-gray-400 mt-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 inline-block mr-2"></div>
                    Sheily está pensando...
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="flex-shrink-0 flex space-x-2">
                <select
                  value={selectedBranch}
                  onChange={(e) => setSelectedBranch(e.target.value)}
                  className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs"
                >
                  {branches.map(branch => (
                    <option key={branch.id} value={branch.name}>
                      {branch.name.split(' ')[0]}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Pregunta a Sheily..."
                  className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  onClick={sendChatMessage}
                  disabled={isChatLoading}
                  className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs font-medium disabled:opacity-50"
                >
                  📤
                </button>
              </div>
            </div>
          </div>


          <div className="col-span-3 row-span-3 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-yellow-400 mb-1">🪙 Tokens SHEILY</h3>
            </div>
            <div className="flex-1 text-xs">
              <div className="text-center mb-4">
                <p className="text-2xl font-bold text-yellow-400">{tokenBalance.toLocaleString()}</p>
                <p className="text-gray-400">Tokens disponibles</p>
              </div>
              <div className="space-y-1">
                <div className="bg-gray-700 rounded p-2">
                  <p className="text-xs">+50 tokens - Ejercicio completado</p>
                </div>
                <div className="bg-gray-700 rounded p-2">
                  <p className="text-xs">+25 tokens - Chat premium</p>
                </div>
                <div className="bg-gray-700 rounded p-2">
                  <p className="text-xs">-10 tokens - Stake DAO</p>
                </div>
              </div>
            </div>
          </div>

          {/* Fila 2 - Blockchain y Gobernanza */}
          <div className="col-span-3 row-span-1 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-purple-400 mb-1">👻 Phantom Wallet</h3>
            </div>
            <div className="flex-1 text-xs">
              {phantomWallet.connected ? (
                <div>
                  <div className="bg-gray-700 rounded p-2 mb-2">
                    <p className="text-gray-400">Dirección</p>
                    <p className="font-mono text-xs">{phantomWallet.address}</p>
                  </div>
                  <div className="bg-gray-700 rounded p-2 mb-2">
                    <p className="text-gray-400">Balance</p>
                    <p className="text-lg font-bold text-green-400">{phantomWallet.balance} SOL</p>
                  </div>
                  <button
                    onClick={disconnectPhantom}
                    className="w-full bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-xs"
                  >
                    Desconectar
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-gray-400 mb-3">No conectado</p>
                  <button
                    onClick={connectPhantom}
                    className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded text-xs"
                  >
                    Conectar Phantom
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="col-span-3 row-span-1 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-orange-400 mb-1">🏛️ Gobernanza DAO</h3>
            </div>
            <div className="flex-1 text-xs">
              <div className="bg-gray-700 rounded p-2 mb-2">
                <p className="text-gray-400">Propuestas activas</p>
                <p className="text-lg font-bold">3</p>
              </div>
              <div className="space-y-1">
                <div className="bg-gray-700 rounded p-2">
                  <p className="text-xs">💡 Nueva rama IA - Votar</p>
                </div>
                <div className="bg-gray-700 rounded p-2">
                  <p className="text-xs">⚡ Aumento tokens diarios</p>
                </div>
              </div>
              <button className="w-full bg-orange-600 hover:bg-orange-700 px-3 py-1 rounded text-xs mt-2">
                Votar
              </button>
            </div>
          </div>

          {/* Fila 3 - IA y Entrenamiento */}
          <div className="col-span-4 row-span-1 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-cyan-400 mb-1">🌿 35 Ramas IA</h3>
            </div>
            <div className="flex-1 overflow-y-auto text-xs">
              {branches.map(branch => (
                <div key={branch.id} className="bg-gray-700 rounded p-2 mb-2">
                  <p className="font-semibold text-cyan-400">{branch.name}</p>
                  <p className="text-gray-400 text-xs mb-1">{branch.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {branch.keywords.slice(0, 2).map((keyword, idx) => (
                      <span key={idx} className="bg-cyan-600 text-xs px-1 py-0.5 rounded">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-4 row-span-1 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-pink-400 mb-1">🎓 Entrenamiento</h3>
            </div>
            <div className="flex-1 text-xs">
              <div className="bg-gray-700 rounded p-2 mb-2">
                <p className="text-gray-400">Ejercicio actual</p>
                <p className="font-semibold">Machine Learning Básico</p>
                <p className="text-gray-400">Progreso: 75%</p>
                <div className="w-full bg-gray-600 rounded-full h-2 mt-1">
                  <div className="bg-pink-400 h-2 rounded-full" style={{width: '75%'}}></div>
                </div>
              </div>
              <div className="space-y-1">
                <button className="w-full bg-pink-600 hover:bg-pink-700 px-3 py-1 rounded text-xs">
                  Completar Ejercicio
                </button>
                <button className="w-full bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-xs">
                  Nuevo Ejercicio
                </button>
              </div>
            </div>
          </div>

          <div className="col-span-4 row-span-1 bg-gray-800 rounded-lg p-3 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-2">
              <h3 className="text-sm font-semibold text-indigo-400 mb-1">📈 Analytics</h3>
            </div>
            <div className="flex-1 text-xs">
              <div className="grid grid-cols-2 gap-2 mb-2">
                <div className="bg-gray-700 rounded p-2 text-center">
                  <p className="text-gray-400">Chats hoy</p>
                  <p className="text-lg font-bold">47</p>
                </div>
                <div className="bg-gray-700 rounded p-2 text-center">
                  <p className="text-gray-400">Ejercicios</p>
                  <p className="text-lg font-bold">12</p>
                </div>
              </div>
              <div className="bg-gray-700 rounded p-2">
                <p className="text-gray-400 mb-1">Rendimiento IA</p>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-600 rounded-full h-2">
                    <div className="bg-indigo-400 h-2 rounded-full" style={{width: '89%'}}></div>
                  </div>
                  <span className="text-xs">89%</span>
                </div>
              </div>
            </div>
          </div>


          <div className="col-span-4 row-span-1 bg-gray-800 rounded-lg p-2 flex flex-col overflow-hidden">
            <div className="flex-shrink-0 mb-1">
              <h4 className="text-xs font-semibold text-purple-400">⚙️ Configuración</h4>
            </div>
            <div className="flex-1 text-xs">
              <div className="grid grid-cols-3 gap-1">
                <button className="bg-purple-600 hover:bg-purple-700 px-2 py-1 rounded text-xs">
                  Tema
                </button>
                <button className="bg-purple-600 hover:bg-purple-700 px-2 py-1 rounded text-xs">
                  Idioma
                </button>
                <button className="bg-purple-600 hover:bg-purple-700 px-2 py-1 rounded text-xs">
                  Notif
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
