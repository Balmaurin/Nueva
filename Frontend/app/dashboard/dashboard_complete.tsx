'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

// Interfaces del sistema Sheily AI
interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  tokens: number;
  level: number;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login?: string;
}

interface ChatMessage {
  id: number;
  session_id: string;
  message: string;
  is_user: boolean;
  tokens_used: number;
  created_at: string;
}

interface Branch {
  id: number;
  name: string;
  description: string;
  keywords: string[];
  enabled: boolean;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  uptime: string;
  active_connections: number;
  total_requests: number;
  error_rate: number;
  timestamp: string;
}

export default function SheilyDashboard() {
  const router = useRouter();

  // Estados principales
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentSection, setCurrentSection] = useState('overview');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Estados de usuario y datos
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);

  // Estados de chat
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState('general');
  const chatMessagesRef = useRef<HTMLDivElement>(null);

  // Estados de configuración
  const [userSettings, setUserSettings] = useState({
    theme: 'dark',
    language: 'es',
    notifications: true,
    autoSave: true,
    soundEnabled: false
  });

  // Inicialización
  useEffect(() => {
    checkAuthentication();
    loadInitialData();
  }, []);

  const checkAuthentication = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/login');
        return;
      }

      setAccessToken(token);

      // Verificar token con API
      const response = await fetch('http://localhost:8002/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setIsAuthenticated(true);
      } else {
        // Token inválido, intentar refresh
        await refreshToken();
      }
    } catch (error) {
      console.error('Error de autenticación:', error);
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        router.push('/login');
        return;
      }

      const response = await fetch('http://localhost:8002/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        setAccessToken(data.access_token);
        setIsAuthenticated(true);
      } else {
        router.push('/login');
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      router.push('/login');
    }
  };

  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadBranches(),
        loadSystemMetrics()
      ]);
    } catch (error) {
      console.error('Error cargando datos iniciales:', error);
    }
  };

  const loadBranches = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/branches');
      if (response.ok) {
        const data = await response.json();
        setBranches(data.branches);
      }
    } catch (error) {
      console.error('Error cargando ramas:', error);
    }
  };

  const loadSystemMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/system/metrics');
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Error cargando métricas:', error);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !accessToken) return;

    const message = chatInput.trim();
    setChatInput('');
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:8002/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          message: message,
          branch: selectedBranch
        })
      });

      if (response.ok) {
        const data = await response.json();

        // Agregar mensaje del usuario y respuesta de Sheily
        const userMessage: ChatMessage = {
          id: Date.now(),
          session_id: 'current',
          message: message,
          is_user: true,
          tokens_used: 0,
          created_at: new Date().toISOString()
        };

        const aiMessage: ChatMessage = {
          id: Date.now() + 1,
          session_id: 'current',
          message: data.response,
          is_user: false,
          tokens_used: data.tokens_used,
          created_at: new Date().toISOString()
        };

        setChatMessages(prev => [...prev, userMessage, aiMessage]);

        // Scroll to bottom
        setTimeout(() => {
          if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
          }
        }, 100);

      } else {
        console.error('Error en respuesta de chat');
      }
    } catch (error) {
      console.error('Error enviando mensaje:', error);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
    setUser(null);
    router.push('/login');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Redirigirá al login
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-gray-800 transition-all duration-300 border-r border-gray-700`}>
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <h1 className="text-xl font-bold text-blue-400">Sheily AI</h1>
            )}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="text-gray-400 hover:text-white"
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>
          </div>
        </div>

        <nav className="p-4">
          <div className="space-y-2">
            {[
              { id: 'overview', label: 'Vista General', icon: '📊' },
              { id: 'chat', label: 'Chat con Sheily', icon: '💬' },
              { id: 'branches', label: 'Ramas Especializadas', icon: '🌿' },
              { id: 'training', label: 'Entrenamiento', icon: '🎓' },
              { id: 'tokens', label: 'Tokens SHEILY', icon: '🪙' },
              { id: 'blockchain', label: 'Blockchain', icon: '⛓️' },
              { id: 'settings', label: 'Configuración', icon: '⚙️' }
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setCurrentSection(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  currentSection === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>
        </nav>

        {/* Usuario */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            {!sidebarCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.username}</p>
                <p className="text-xs text-gray-400">{user?.tokens} tokens</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="text-gray-400 hover:text-red-400"
              title="Cerrar sesión"
            >
              🚪
            </button>
          </div>
        </div>
      </div>

      {/* Contenido Principal */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold capitalize">
              {currentSection === 'overview' ? 'Vista General' :
               currentSection === 'chat' ? 'Chat con Sheily' :
               currentSection === 'branches' ? 'Ramas Especializadas' :
               currentSection === 'training' ? 'Entrenamiento Interactivo' :
               currentSection === 'tokens' ? 'Sistema de Tokens' :
               currentSection === 'blockchain' ? 'Blockchain & Wallets' :
               currentSection === 'settings' ? 'Configuración' : currentSection}
            </h2>

            <div className="flex items-center space-x-4">
              {/* Notificaciones */}
              <button className="text-gray-400 hover:text-white">
                🔔
              </button>

              {/* Tema */}
              <button className="text-gray-400 hover:text-white">
                {userSettings.theme === 'dark' ? '🌙' : '☀️'}
              </button>
            </div>
          </div>
        </header>

        {/* Contenido */}
        <main className="flex-1 p-6 overflow-auto">
          {currentSection === 'overview' && <OverviewSection user={user} systemMetrics={systemMetrics} />}
          {currentSection === 'chat' && (
            <ChatSection
              messages={chatMessages}
              input={chatInput}
              setInput={setChatInput}
              onSend={sendChatMessage}
              onKeyPress={handleKeyPress}
              isLoading={isChatLoading}
              selectedBranch={selectedBranch}
              setSelectedBranch={setSelectedBranch}
              branches={branches}
              messagesRef={chatMessagesRef}
            />
          )}
          {currentSection === 'branches' && <BranchesSection branches={branches} />}
          {currentSection === 'training' && <TrainingSection />}
          {currentSection === 'tokens' && <TokensSection user={user} />}
          {currentSection === 'blockchain' && <BlockchainSection />}
          {currentSection === 'settings' && (
            <SettingsSection
              user={user}
              settings={userSettings}
              setSettings={setUserSettings}
            />
          )}
        </main>
      </div>
    </div>
  );
}

// Componente de Vista General
function OverviewSection({ user, systemMetrics }: { user: User | null, systemMetrics: SystemMetrics | null }) {
  return (
    <div className="space-y-6">
      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-500 rounded-lg">
              <span className="text-2xl">👤</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-400">Usuario</p>
              <p className="text-xl font-semibold">{user?.username}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-500 rounded-lg">
              <span className="text-2xl">🪙</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-400">Tokens SHEILY</p>
              <p className="text-xl font-semibold">{user?.tokens}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-500 rounded-lg">
              <span className="text-2xl">📈</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-400">Nivel</p>
              <p className="text-xl font-semibold">{user?.level}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-500 rounded-lg">
              <span className="text-2xl">🌿</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-400">Ramas</p>
              <p className="text-xl font-semibold">35</p>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas del sistema */}
      {systemMetrics && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Métricas del Sistema</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-400">{systemMetrics.cpu_usage.toFixed(1)}%</p>
              <p className="text-sm text-gray-400">CPU</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400">{systemMetrics.memory_usage.toFixed(1)}%</p>
              <p className="text-sm text-gray-400">Memoria</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-400">{systemMetrics.disk_usage.toFixed(1)}%</p>
              <p className="text-sm text-gray-400">Disco</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-400">{systemMetrics.active_connections}</p>
              <p className="text-sm text-gray-400">Conexiones</p>
            </div>
          </div>
        </div>
      )}

      {/* Actividad reciente */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Actividad Reciente</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg">
            <span className="text-green-400">💬</span>
            <div className="flex-1">
              <p className="text-sm">Nueva conversación iniciada</p>
              <p className="text-xs text-gray-400">Hace 5 minutos</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg">
            <span className="text-blue-400">🎓</span>
            <div className="flex-1">
              <p className="text-sm">Ejercicio completado en Matemáticas</p>
              <p className="text-xs text-gray-400">Hace 15 minutos</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg">
            <span className="text-yellow-400">🪙</span>
            <div className="flex-1">
              <p className="text-sm">10 tokens SHEILY ganados</p>
              <p className="text-xs text-gray-400">Hace 30 minutos</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Chat
function ChatSection({
  messages,
  input,
  setInput,
  onSend,
  onKeyPress,
  isLoading,
  selectedBranch,
  setSelectedBranch,
  branches,
  messagesRef
}: {
  messages: ChatMessage[];
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  isLoading: boolean;
  selectedBranch: string;
  setSelectedBranch: (branch: string) => void;
  branches: Branch[];
  messagesRef: React.RefObject<HTMLDivElement>;
}) {
  return (
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
        ref={messagesRef}
        className="flex-1 bg-gray-800 rounded-lg p-4 overflow-y-auto mb-4 min-h-96"
      >
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">¡Hola! Soy Sheily AI 🤖</p>
            <p>Selecciona una rama especializada y comienza a chatear.</p>
            <p className="text-sm mt-2">Puedo ayudarte con 35 especializaciones diferentes.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map(message => (
              <div key={message.id} className={`flex ${message.is_user ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.is_user
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-100'
                }`}>
                  <p className="text-sm">{message.message}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {message.tokens_used > 0 && `${message.tokens_used} tokens`}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-700 text-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                    <span className="text-sm">Sheily está pensando...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={onKeyPress}
          placeholder="Escribe tu mensaje aquí..."
          className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          onClick={onSend}
          disabled={isLoading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-medium transition-colors"
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </div>
    </div>
  );
}

// Componente de Ramas
function BranchesSection({ branches }: { branches: Branch[] }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {branches.map(branch => (
          <div key={branch.id} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors">
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-3">🌿</span>
              <h3 className="text-lg font-semibold">
                {branch.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h3>
            </div>
            <p className="text-gray-400 text-sm mb-3">{branch.description}</p>
            <div className="flex flex-wrap gap-1">
              {branch.keywords.slice(0, 3).map(keyword => (
                <span key={keyword} className="bg-blue-600 text-xs px-2 py-1 rounded-full">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Componentes placeholder para otras secciones
function TrainingSection() {
  return (
    <div className="text-center py-12">
      <span className="text-6xl mb-4 block">🎓</span>
      <h3 className="text-xl font-semibold mb-2">Sistema de Entrenamiento Interactivo</h3>
      <p className="text-gray-400">Completa ejercicios en diferentes ramas para ganar tokens SHEILY</p>
      <div className="mt-6 bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
        <p className="text-sm text-gray-500">Funcionalidad en desarrollo...</p>
      </div>
    </div>
  );
}

function TokensSection({ user }: { user: User | null }) {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Balance de Tokens SHEILY</h3>
        <div className="text-center">
          <span className="text-4xl mb-2 block">🪙</span>
          <p className="text-3xl font-bold text-yellow-400">{user?.tokens}</p>
          <p className="text-gray-400">Tokens disponibles</p>
        </div>
      </div>
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Transacciones Recientes</h3>
        <div className="text-center text-gray-500 py-8">
          <p>No hay transacciones recientes</p>
        </div>
      </div>
    </div>
  );
}

function BlockchainSection() {
  return (
    <div className="text-center py-12">
      <span className="text-6xl mb-4 block">⛓️</span>
      <h3 className="text-xl font-semibold mb-2">Integración Blockchain</h3>
      <p className="text-gray-400">Conecta tu wallet Phantom y gestiona tokens en Solana</p>
      <div className="mt-6 bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
        <p className="text-sm text-gray-500">Funcionalidad en desarrollo...</p>
      </div>
    </div>
  );
}

function SettingsSection({ user, settings, setSettings }: {
  user: User | null;
  settings: any;
  setSettings: (settings: any) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Perfil de Usuario</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nombre de usuario</label>
            <p className="bg-gray-700 px-3 py-2 rounded-lg">{user?.username}</p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <p className="bg-gray-700 px-3 py-2 rounded-lg">{user?.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Nombre completo</label>
            <p className="bg-gray-700 px-3 py-2 rounded-lg">{user?.full_name || 'No especificado'}</p>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Configuración</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">Tema oscuro</span>
            <button
              onClick={() => setSettings({...settings, theme: settings.theme === 'dark' ? 'light' : 'dark'})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.theme === 'dark' ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.theme === 'dark' ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Notificaciones</span>
            <button
              onClick={() => setSettings({...settings, notifications: !settings.notifications})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.notifications ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.notifications ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
