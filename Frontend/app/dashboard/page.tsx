'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

// ===== DASHBOARD SHEILY AI - PESTAÑAS FUNCIONALES =====
// Chat, Ejercicios, Dataset, Entrenamientos, Wallet, Configuración

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  // Estados para Chat
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState('general');
  const chatMessagesRef = useRef(null);

  // Estados para Wallet
  const [phantomWallet, setPhantomWallet] = useState({
    connected: false,
    address: '',
    balance: 0
  });
  const [tokenBalance, setTokenBalance] = useState(150);

  // Estados para Ejercicios
  const [currentExercise, setCurrentExercise] = useState(null);
  const [exerciseAnswer, setExerciseAnswer] = useState('');
  const [isSubmittingExercise, setIsSubmittingExercise] = useState(false);

  // Estados para Dataset
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);

  // Estados para Entrenamientos
  const [trainingJobs, setTrainingJobs] = useState([]);
  const [currentTraining, setCurrentTraining] = useState(null);

  // Datos simulados
  const branches = [
    { id: '1', name: 'Machine Learning', description: 'Aprendizaje automático' },
    { id: '2', name: 'Natural Language Processing', description: 'Procesamiento de lenguaje' },
    { id: '3', name: 'Computer Vision', description: 'Visión por computadora' }
  ];

  const exercises = [
    {
      id: 1,
      title: 'Introducción a Machine Learning',
      description: 'Aprende los conceptos básicos del aprendizaje automático',
      type: 'multiple_choice',
      question: '¿Cuál es el objetivo principal del aprendizaje supervisado?',
      options: ['Encontrar patrones ocultos', 'Predecir valores basados en datos etiquetados', 'Reducir dimensionalidad', 'Clustering de datos'],
      correctAnswer: 1,
      completed: false,
      reward: 50
    },
    {
      id: 2,
      title: 'Redes Neuronales Básicas',
      description: 'Comprende cómo funcionan las redes neuronales',
      type: 'text_input',
      question: 'Explica brevemente qué es una función de activación en una red neuronal.',
      completed: false,
      reward: 75
    }
  ];

  const sampleDatasets = [
    {
      id: 1,
      name: 'ML Fundamentals Dataset',
      description: 'Conjunto de datos para ejercicios básicos de ML',
      size: '2.3 MB',
      records: 15420,
      created: '2024-01-15',
      branch: 'Machine Learning'
    },
    {
      id: 2,
      name: 'NLP Conversations',
      description: 'Dataset de conversaciones para fine-tuning de modelos de lenguaje',
      size: '45.7 MB',
      records: 89234,
      created: '2024-01-20',
      branch: 'Natural Language Processing'
    }
  ];

  const trainingHistory = [
    {
      id: 1,
      name: 'ML Model v2.1',
      branch: 'Machine Learning',
      status: 'completed',
      accuracy: 94.2,
      epochs: 150,
      datasetSize: 15420,
      completedAt: '2024-01-22 14:30'
    },
    {
      id: 2,
      name: 'NLP Chat Model',
      branch: 'Natural Language Processing',
      status: 'running',
      accuracy: null,
      epochs: 89,
      datasetSize: 89234,
      startedAt: '2024-01-23 09:15'
    }
  ];

  // Funciones del Chat
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

  // Funciones de Wallet
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

  // Funciones de Ejercicios
  const submitExercise = async (exerciseId, answer) => {
    setIsSubmittingExercise(true);
    // Simular verificación de respuesta
    setTimeout(() => {
      const exercise = exercises.find(e => e.id === exerciseId);
      if (exercise) {
        // Marcar como completado y dar recompensa
        setTokenBalance(prev => prev + exercise.reward);
        setCurrentExercise(null);
        setExerciseAnswer('');
      }
      setIsSubmittingExercise(false);
    }, 2000);
  };

  // Funciones de Dataset
  const generateDataset = () => {
    const newDataset = {
      id: Date.now(),
      name: `Dataset ${datasets.length + 1}`,
      description: 'Dataset generado automáticamente',
      size: '1.2 MB',
      records: Math.floor(Math.random() * 10000) + 5000,
      created: new Date().toISOString().split('T')[0],
      branch: selectedBranch
    };
    setDatasets(prev => [...prev, newDataset]);
  };

  // Funciones de Entrenamiento
  const startTraining = (datasetId) => {
    const dataset = datasets.find(d => d.id === datasetId) || sampleDatasets.find(d => d.id === datasetId);
    if (dataset) {
      const newTraining = {
        id: Date.now(),
        name: `Training ${dataset.name}`,
        datasetId: dataset.id,
        branch: dataset.branch,
        status: 'running',
        progress: 0,
        startedAt: new Date().toLocaleString()
      };
      setTrainingJobs(prev => [...prev, newTraining]);
      setCurrentTraining(newTraining);

      // Simular progreso de entrenamiento
      const interval = setInterval(() => {
        setTrainingJobs(prev => prev.map(job =>
          job.id === newTraining.id
            ? { ...job, progress: Math.min(job.progress + Math.random() * 10, 100) }
            : job
        ));
      }, 2000);

      setTimeout(() => {
        clearInterval(interval);
        setTrainingJobs(prev => prev.map(job =>
          job.id === newTraining.id
            ? { ...job, status: 'completed', progress: 100 }
            : job
        ));
        setCurrentTraining(null);
      }, 30000);
    }
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

  const tabs = [
    { id: 'overview', label: '🏠 Sheily AI', description: 'Centro de control principal' },
    { id: 'chat', label: '💬 Chat', description: 'Conversación con IA' },
    { id: 'exercises', label: '📚 Ejercicios', description: 'Aprendizaje interactivo' },
    { id: 'datasets', label: '📊 Dataset', description: 'Gestión de datos' },
    { id: 'training', label: '🎯 Entrenamientos', description: 'Fine-tuning de modelos' },
    { id: 'wallet', label: '👻 Wallet', description: 'Phantom & tokens' },
    { id: 'settings', label: '⚙️ Configuración', description: 'Ajustes del sistema' }
  ];

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">🚀</span>
              <div>
                <h1 className="text-2xl font-bold text-blue-400">Sheily AI</h1>
                <p className="text-sm text-gray-400">Sistema de Inteligencia Artificial Avanzado</p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-400">Usuario</p>
              <p className="font-medium">{user?.username || 'Usuario'}</p>
            </div>
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <span>👤</span>
            </div>
          </div>
        </div>
      </header>

      {/* Pestañas */}
      <nav className="bg-gray-800 px-6 py-3 border-b border-gray-700">
        <div className="flex space-x-2 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-shrink-0 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              }`}
            >
              <div className="text-center">
                <div className="text-lg">{tab.label}</div>
                <div className="text-xs opacity-75">{tab.description}</div>
              </div>
            </button>
          ))}
        </div>
      </nav>

      {/* Contenido Principal */}
      <main className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div className="text-center py-12">
              <h2 className="text-4xl font-bold text-blue-400 mb-4">Bienvenido a Sheily AI</h2>
              <p className="text-xl text-gray-400 mb-8">Tu plataforma completa de inteligencia artificial</p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <div className="text-center">
                    <span className="text-5xl mb-4 block">💬</span>
                    <h3 className="text-xl font-semibold mb-2">Chat Inteligente</h3>
                    <p className="text-gray-400 mb-4">Conversación avanzada con Llama 3.2 Q4</p>
                    <button
                      onClick={() => setActiveTab('chat')}
                      className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium"
                    >
                      Ir al Chat
                    </button>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <div className="text-center">
                    <span className="text-5xl mb-4 block">📚</span>
                    <h3 className="text-xl font-semibold mb-2">Sistema de Ejercicios</h3>
                    <p className="text-gray-400 mb-4">Aprendizaje interactivo con recompensas</p>
                    <button
                      onClick={() => setActiveTab('exercises')}
                      className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium"
                    >
                      Hacer Ejercicios
                    </button>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <div className="text-center">
                    <span className="text-5xl mb-4 block">🎯</span>
                    <h3 className="text-xl font-semibold mb-2">Entrenamiento LoRA</h3>
                    <p className="text-gray-400 mb-4">Fine-tuning personalizado de modelos</p>
                    <button
                      onClick={() => setActiveTab('training')}
                      className="bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-lg font-medium"
                    >
                      Entrenar Modelos
                    </button>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <div className="text-center">
                    <span className="text-5xl mb-4 block">📊</span>
                    <h3 className="text-xl font-semibold mb-2">Dataset Manager</h3>
                    <p className="text-gray-400 mb-4">Gestión completa de conjuntos de datos</p>
                    <button
                      onClick={() => setActiveTab('datasets')}
                      className="bg-orange-600 hover:bg-orange-700 px-6 py-2 rounded-lg font-medium"
                    >
                      Gestionar Datos
                    </button>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <div className="text-center">
                    <span className="text-5xl mb-4 block">👻</span>
                    <h3 className="text-xl font-semibold mb-2">Phantom Wallet</h3>
                    <p className="text-gray-400 mb-4">Blockchain Solana integrada</p>
                    <button
                      onClick={() => setActiveTab('wallet')}
                      className="bg-indigo-600 hover:bg-indigo-700 px-6 py-2 rounded-lg font-medium"
                    >
                      Gestionar Wallet
                    </button>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <div className="text-center">
                    <span className="text-5xl mb-4 block">⚙️</span>
                    <h3 className="text-xl font-semibold mb-2">Configuración</h3>
                    <p className="text-gray-400 mb-4">Personaliza tu experiencia</p>
                    <button
                      onClick={() => setActiveTab('settings')}
                      className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded-lg font-medium"
                    >
                      Configurar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-blue-400">💬 Chat con Sheily AI</h2>
                  <p className="text-gray-400">Conversación inteligente con Llama 3.2 Q4</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-400">Tokens disponibles</p>
                  <p className="text-lg font-bold text-yellow-400">{tokenBalance}</p>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Rama especializada:</label>
                <select
                  value={selectedBranch}
                  onChange={(e) => setSelectedBranch(e.target.value)}
                  className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 w-full max-w-md"
                >
                  <option value="general">General</option>
                  {branches.map(branch => (
                    <option key={branch.id} value={branch.name}>
                      {branch.name}
                    </option>
                  ))}
                </select>
              </div>

              <div
                ref={chatMessagesRef}
                className="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto mb-4"
              >
                {chatMessages.length === 0 ? (
                  <div className="text-center text-gray-400 mt-16">
                    <p className="text-lg mb-2">¡Hola! Soy Sheily AI 🤖</p>
                    <p>Pregúntame cualquier cosa sobre las 35 ramas especializadas de IA</p>
                  </div>
                ) : (
                  chatMessages.map(msg => (
                    <div key={msg.id} className={`mb-4 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                      <div className={`inline-block p-3 rounded-lg max-w-2xl ${
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
          </div>
        )}

        {activeTab === 'exercises' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-green-400">📚 Sistema de Ejercicios</h2>
                  <p className="text-gray-400">Aprendizaje interactivo con recompensas en tokens SHEILY</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-400">Tokens ganados</p>
                  <p className="text-lg font-bold text-yellow-400">{tokenBalance}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Ejercicios Disponibles</h3>
                  <div className="space-y-4">
                    {exercises.map(exercise => (
                      <div key={exercise.id} className="bg-gray-700 rounded-lg p-4">
                        <h4 className="font-semibold mb-2">{exercise.title}</h4>
                        <p className="text-sm text-gray-400 mb-3">{exercise.description}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-yellow-400">+{exercise.reward} tokens</span>
                          <button
                            onClick={() => setCurrentExercise(exercise)}
                            className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm font-medium"
                          >
                            Resolver
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  {currentExercise ? (
                    <div className="bg-gray-700 rounded-lg p-4">
                      <h3 className="font-semibold mb-4">{currentExercise.title}</h3>
                      <p className="text-sm mb-4">{currentExercise.question}</p>

                      {currentExercise.type === 'multiple_choice' && (
                        <div className="space-y-2 mb-4">
                          {currentExercise.options.map((option, index) => (
                            <label key={index} className="flex items-center space-x-2">
                              <input
                                type="radio"
                                name="answer"
                                value={index}
                                onChange={(e) => setExerciseAnswer(e.target.value)}
                                className="text-green-600"
                              />
                              <span className="text-sm">{option}</span>
                            </label>
                          ))}
                        </div>
                      )}

                      {currentExercise.type === 'text_input' && (
                        <textarea
                          value={exerciseAnswer}
                          onChange={(e) => setExerciseAnswer(e.target.value)}
                          placeholder="Escribe tu respuesta aquí..."
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white mb-4"
                          rows={4}
                        />
                      )}

                      <div className="flex space-x-2">
                        <button
                          onClick={() => submitExercise(currentExercise.id, exerciseAnswer)}
                          disabled={isSubmittingExercise || !exerciseAnswer}
                          className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded font-medium disabled:opacity-50"
                        >
                          {isSubmittingExercise ? 'Verificando...' : 'Enviar Respuesta'}
                        </button>
                        <button
                          onClick={() => setCurrentExercise(null)}
                          className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded font-medium"
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-700 rounded-lg p-8 text-center">
                      <span className="text-4xl mb-4 block">📝</span>
                      <p className="text-gray-400">Selecciona un ejercicio para comenzar</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'datasets' && (
          <div className="max-w-6xl mx-auto">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-orange-400">📊 Dataset Manager</h2>
                  <p className="text-gray-400">Gestión completa de conjuntos de datos para entrenamiento</p>
                </div>
                <button
                  onClick={generateDataset}
                  className="bg-orange-600 hover:bg-orange-700 px-6 py-3 rounded-lg font-medium"
                >
                  ➕ Generar Dataset
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Datasets Disponibles</h3>
                  <div className="space-y-4">
                    {[...sampleDatasets, ...datasets].map(dataset => (
                      <div key={dataset.id} className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{dataset.name}</h4>
                          <span className="text-xs bg-orange-600 px-2 py-1 rounded">{dataset.branch}</span>
                        </div>
                        <p className="text-sm text-gray-400 mb-2">{dataset.description}</p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{dataset.records.toLocaleString()} registros</span>
                          <span>{dataset.size}</span>
                          <span>{dataset.created}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Estadísticas</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-700 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-orange-400">{[...sampleDatasets, ...datasets].length}</p>
                      <p className="text-sm text-gray-400">Total Datasets</p>
                    </div>
                    <div className="bg-gray-700 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-blue-400">
                        {[...sampleDatasets, ...datasets].reduce((sum, d) => sum + d.records, 0).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-400">Registros Totales</p>
                    </div>
                  </div>

                  <div className="mt-6">
                    <h4 className="font-semibold mb-3">Distribución por Rama</h4>
                    <div className="space-y-2">
                      {['Machine Learning', 'Natural Language Processing', 'Computer Vision'].map(branch => {
                        const count = [...sampleDatasets, ...datasets].filter(d => d.branch === branch).length;
                        return (
                          <div key={branch} className="flex items-center justify-between">
                            <span className="text-sm">{branch}</span>
                            <span className="text-sm font-bold">{count}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'training' && (
          <div className="max-w-6xl mx-auto">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-purple-400">🎯 Sistema de Entrenamientos LoRA</h2>
                  <p className="text-gray-400">Fine-tuning personalizado de modelos de IA</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-400">Entrenamientos activos</p>
                  <p className="text-lg font-bold text-purple-400">
                    {trainingHistory.filter(t => t.status === 'running').length}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Iniciar Nuevo Entrenamiento</h3>
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-2">Seleccionar Dataset:</label>
                      <select
                        value={selectedDataset || ''}
                        onChange={(e) => setSelectedDataset(parseInt(e.target.value))}
                        className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2"
                      >
                        <option value="">Elegir dataset...</option>
                        {[...sampleDatasets, ...datasets].map(dataset => (
                          <option key={dataset.id} value={dataset.id}>
                            {dataset.name} ({dataset.records.toLocaleString()} registros)
                          </option>
                        ))}
                      </select>
                    </div>

                    <button
                      onClick={() => selectedDataset && startTraining(selectedDataset)}
                      disabled={!selectedDataset || currentTraining}
                      className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded font-medium disabled:opacity-50"
                    >
                      🚀 Iniciar Entrenamiento LoRA
                    </button>
                  </div>
                </div>

                <div>
                  {currentTraining ? (
                    <div className="bg-gray-700 rounded-lg p-4">
                      <h4 className="font-semibold mb-3">Entrenamiento en Progreso</h4>
                      <div className="mb-3">
                        <div className="flex justify-between text-sm mb-1">
                          <span>{currentTraining.name}</span>
                          <span>{Math.round(currentTraining.progress)}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-3">
                          <div
                            className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                            style={{width: `${currentTraining.progress}%`}}
                          ></div>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400">Iniciado: {currentTraining.startedAt}</p>
                    </div>
                  ) : (
                    <div className="bg-gray-700 rounded-lg p-8 text-center">
                      <span className="text-4xl mb-4 block">🎯</span>
                      <p className="text-gray-400">Selecciona un dataset para iniciar el entrenamiento</p>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Historial de Entrenamientos</h3>
                <div className="space-y-3">
                  {trainingHistory.map(training => (
                    <div key={training.id} className="bg-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{training.name}</h4>
                        <span className={`text-xs px-2 py-1 rounded ${
                          training.status === 'completed' ? 'bg-green-600' :
                          training.status === 'running' ? 'bg-blue-600' : 'bg-red-600'
                        }`}>
                          {training.status === 'completed' ? 'Completado' :
                           training.status === 'running' ? 'En Progreso' : 'Error'}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Rama</p>
                          <p>{training.branch}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Dataset</p>
                          <p>{training.datasetSize.toLocaleString()} registros</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Épocas</p>
                          <p>{training.epochs}</p>
                        </div>
                        {training.accuracy && (
                          <div>
                            <p className="text-gray-400">Precisión</p>
                            <p className="text-green-400">{training.accuracy}%</p>
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        {training.completedAt ? `Completado: ${training.completedAt}` : `Iniciado: ${training.startedAt}`}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'wallet' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-indigo-400">👻 Phantom Wallet & Tokens</h2>
                  <p className="text-gray-400">Gestión completa de blockchain y criptomonedas</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-400">Balance Total</p>
                  <p className="text-lg font-bold text-green-400">{phantomWallet.balance + tokenBalance} USD</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Phantom Wallet</h3>
                  {phantomWallet.connected ? (
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium text-gray-400">Dirección</p>
                        <p className="font-mono text-sm bg-gray-600 p-2 rounded break-all">{phantomWallet.address}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-400">Balance SOL</p>
                        <p className="text-2xl font-bold text-green-400">{phantomWallet.balance} SOL</p>
                      </div>
                      <button
                        onClick={disconnectPhantom}
                        className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium"
                      >
                        🔌 Desconectar Wallet
                      </button>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <span className="text-4xl mb-4 block">👻</span>
                      <p className="text-gray-400 mb-4">No hay wallet conectada</p>
                      <button
                        onClick={connectPhantom}
                        className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-medium"
                      >
                        🔗 Conectar Phantom
                      </button>
                    </div>
                  )}
                </div>

                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Tokens SHEILY</h3>
                  <div className="text-center mb-6">
                    <p className="text-4xl font-bold text-yellow-400 mb-2">{tokenBalance.toLocaleString()}</p>
                    <p className="text-gray-400">Tokens disponibles</p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-2 bg-gray-600 rounded">
                      <span className="text-sm">Ejercicio completado</span>
                      <span className="text-green-400">+50 SHEILY</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-600 rounded">
                      <span className="text-sm">Chat premium</span>
                      <span className="text-green-400">+25 SHEILY</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-600 rounded">
                      <span className="text-sm">Stake DAO</span>
                      <span className="text-red-400">-10 SHEILY</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Transacciones Recientes</h3>
                <div className="bg-gray-700 rounded-lg overflow-hidden">
                  <div className="p-4 border-b border-gray-600">
                    <div className="grid grid-cols-4 gap-4 text-sm font-medium text-gray-400">
                      <span>Tipo</span>
                      <span>Cantidad</span>
                      <span>Estado</span>
                      <span>Fecha</span>
                    </div>
                  </div>
                  <div className="divide-y divide-gray-600">
                    <div className="p-4 grid grid-cols-4 gap-4 text-sm">
                      <span>Compra SHEILY</span>
                      <span className="text-green-400">+100</span>
                      <span className="text-green-400">Completada</span>
                      <span>2024-01-23</span>
                    </div>
                    <div className="p-4 grid grid-cols-4 gap-4 text-sm">
                      <span>Stake DAO</span>
                      <span className="text-red-400">-50</span>
                      <span className="text-yellow-400">Pendiente</span>
                      <span>2024-01-22</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-300">⚙️ Configuración del Sistema</h2>
                  <p className="text-gray-400">Personaliza tu experiencia en Sheily AI</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Tema</h3>
                    <div className="space-y-3">
                      <button className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium">
                        Tema Oscuro (Actual)
                      </button>
                      <button className="w-full bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-medium">
                        Tema Claro
                      </button>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Idioma</h3>
                    <select className="w-full bg-gray-600 border border-gray-500 rounded-lg px-3 py-2">
                      <option>Español</option>
                      <option>English</option>
                      <option>Français</option>
                      <option>Deutsch</option>
                    </select>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Notificaciones</h3>
                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="mr-2" />
                        <span className="text-sm">Ejercicios completados</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="mr-2" />
                        <span className="text-sm">Nuevos tokens</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Propuestas DAO</span>
                      </label>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Cuenta</h3>
                    <div className="space-y-3">
                      <button className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium">
                        Cambiar Contraseña
                      </button>
                      <button className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium">
                        Cambiar Email
                      </button>
                      <button className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium">
                        Cerrar Sesión
                      </button>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-4">Privacidad</h3>
                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="mr-2" />
                        <span className="text-sm">Guardar historial de chat</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Analytics anónimos</span>
                      </label>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
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
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
