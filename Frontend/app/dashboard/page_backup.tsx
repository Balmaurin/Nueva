'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

// Interfaces completas del sistema Sheily AI
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

interface SheilyToken {
  id: string;
  user_id: string;
  amount: number;
  token_type: 'TRAINING' | 'RESPONSE' | 'INNOVATION' | 'GOVERNANCE' | 'SPECIAL_CONTRIBUTION' | 'LEARNING' | 'DOMAIN_EXPERTISE';
  reason: string;
  blockchain_tx?: string;
  created_at: string;
}

interface TrainingExercise {
  id: number;
  branch_name: string;
  question: string;
  answer: string;
  difficulty: 'easy' | 'medium' | 'hard';
  completed: boolean;
  score: number;
  user_answer?: string;
}

interface BlockchainTransaction {
  id: string;
  type: 'mint' | 'transfer' | 'burn' | 'stake';
  amount: number;
  from_address: string;
  to_address: string;
  tx_hash: string;
  status: 'pending' | 'confirmed' | 'failed';
  timestamp: string;
}

interface GovernanceProposal {
  id: string;
  title: string;
  description: string;
  proposer: string;
  votes_for: number;
  votes_against: number;
  status: 'active' | 'passed' | 'rejected' | 'executed';
  deadline: string;
  created_at: string;
}

interface PhantomWallet {
  connected: boolean;
  address: string;
  balance: number;
  network: 'mainnet-beta' | 'devnet' | 'testnet';
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
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
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // Estados de chat
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState('general');
  const [currentChatSession, setCurrentChatSession] = useState<string | null>(null);
  const chatMessagesRef = useRef<HTMLDivElement>(null);

  // Estados de tokens SHEILY
  const [sheilyTokens, setSheilyTokens] = useState<SheilyToken[]>([]);
  const [tokenTransactions, setTokenTransactions] = useState<SheilyToken[]>([]);
  const [totalTokenBalance, setTotalTokenBalance] = useState(0);

  // Estados de entrenamiento
  const [trainingExercises, setTrainingExercises] = useState<TrainingExercise[]>([]);
  const [currentExercise, setCurrentExercise] = useState<TrainingExercise | null>(null);
  const [exerciseAnswer, setExerciseAnswer] = useState('');
  const [isSubmittingExercise, setIsSubmittingExercise] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState<{[key: string]: {completed: number, total: number}}>({});

  // Estados de blockchain
  const [phantomWallet, setPhantomWallet] = useState<PhantomWallet>({
    connected: false,
    address: '',
    balance: 0,
    network: 'devnet'
  });
  const [blockchainTransactions, setBlockchainTransactions] = useState<BlockchainTransaction[]>([]);
  const [governanceProposals, setGovernanceProposals] = useState<GovernanceProposal[]>([]);

  // Estados de configuración
  const [userSettings, setUserSettings] = useState({
    theme: 'dark',
    language: 'es',
    notifications: true,
    autoSave: true,
    soundEnabled: false,
    twoFactorEnabled: false
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

      const response = await fetch('http://localhost:8000/api/auth/refresh', {
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
        loadSystemMetrics(),
        loadUserTokens(),
        loadTrainingProgress(),
        loadBlockchainData(),
        loadNotifications()
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

  const loadUserTokens = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/tokens/balance', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSheilyTokens(data.tokens || []);
        setTokenTransactions(data.transactions || []);
        setTotalTokenBalance(data.total_balance || 0);
      }
    } catch (error) {
      console.error('Error cargando tokens:', error);
    }
  };

  const loadTrainingProgress = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/training/progress', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTrainingExercises(data.exercises || []);
        setTrainingProgress(data.progress || {});
      }
    } catch (error) {
      console.error('Error cargando progreso de entrenamiento:', error);
    }
  };

  const loadBlockchainData = async () => {
    try {
      // Cargar datos de wallet Phantom
      const walletResponse = await fetch('http://localhost:8002/api/blockchain/wallet', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (walletResponse.ok) {
        const walletData = await walletResponse.json();
        setPhantomWallet(walletData.wallet || phantomWallet);
      }

      // Cargar transacciones blockchain
      const txResponse = await fetch('http://localhost:8002/api/blockchain/transactions', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (txResponse.ok) {
        const txData = await txResponse.json();
        setBlockchainTransactions(txData.transactions || []);
      }

      // Cargar propuestas de gobernanza
      const govResponse = await fetch('http://localhost:8002/api/governance/proposals', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (govResponse.ok) {
        const govData = await govResponse.json();
        setGovernanceProposals(govData.proposals || []);
      }
    } catch (error) {
      console.error('Error cargando datos blockchain:', error);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/notifications', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (error) {
      console.error('Error cargando notificaciones:', error);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !accessToken) return;

    const message = chatInput.trim();
    setChatInput('');
    setIsChatLoading(true);

    try {
      // Usar el chatbot avanzado Sheily (puerto 8005)
      const response = await fetch('http://localhost:8005/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          user_id: user?.id,
          branch: selectedBranch,
          session_id: currentChatSession || `session_${Date.now()}`
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
              { id: 'branches', label: '35 Ramas IA', icon: '🌿' },
              { id: 'training', label: 'Entrenamiento', icon: '🎓' },
              { id: 'memory', label: 'Memoria Inteligente', icon: '🧠' },
              { id: 'embeddings', label: 'Embeddings', icon: '🔍' },
              { id: 'evaluation', label: 'Evaluación IA', icon: '📊' },
              { id: 'reinforcement', label: 'Aprendizaje Refuerzo', icon: '🎯' },
              { id: 'recommendations', label: 'Recomendaciones', icon: '💡' },
              { id: 'tokens', label: 'Tokens SHEILY', icon: '🪙' },
              { id: 'blockchain', label: 'Phantom Wallet', icon: '👻' },
              { id: 'governance', label: 'Gobernanza DAO', icon: '🏛️' },
              { id: 'analytics', label: 'Analytics Avanzado', icon: '📈' },
              { id: 'monitoring', label: 'Monitoreo Sistema', icon: '📊' },
              { id: 'visualization', label: 'Visualización Datos', icon: '📊' },
              { id: 'integrations', label: 'Integraciones', icon: '🔗' },
              { id: 'plugins', label: 'Plugins Sistema', icon: '🔌' },
              { id: 'backup', label: 'Backup Completo', icon: '💾' },
              { id: 'audit', label: 'Auditoría', icon: '🔒' },
              { id: 'deployment', label: 'Despliegue CI/CD', icon: '🚀' },
              { id: 'i18n', label: 'Internacionalización', icon: '🌍' },
              { id: 'benchmark', label: 'Benchmarks', icon: '⚡' },
              { id: 'logs', label: 'Sistema Logs', icon: '📝' },
              { id: 'debugging', label: 'Debugging Tools', icon: '🔧' },
              { id: 'documentation', label: 'Documentación', icon: '📚' },
              { id: 'settings', label: 'Configuración Avanzada', icon: '⚙️' }
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
          {currentSection === 'overview' && <OverviewSection user={user} systemMetrics={systemMetrics} notifications={notifications} />}
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
          {currentSection === 'training' && (
            <TrainingSection
              exercises={trainingExercises}
              currentExercise={currentExercise}
              setCurrentExercise={setCurrentExercise}
              exerciseAnswer={exerciseAnswer}
              setExerciseAnswer={setExerciseAnswer}
              isSubmitting={isSubmittingExercise}
              setIsSubmitting={setIsSubmittingExercise}
              progress={trainingProgress}
            />
          )}
          {currentSection === 'tokens' && (
            <TokensSection
              user={user}
              tokens={sheilyTokens}
              transactions={tokenTransactions}
              totalBalance={totalTokenBalance}
            />
          )}
          {currentSection === 'blockchain' && (
            <BlockchainSection
              wallet={phantomWallet}
              transactions={blockchainTransactions}
              setWallet={setPhantomWallet}
            />
          )}
          {currentSection === 'governance' && (
            <GovernanceSection
              proposals={governanceProposals}
              userTokens={totalTokenBalance}
            />
          )}
          {currentSection === 'memory' && <MemorySection />}
          {currentSection === 'embeddings' && <EmbeddingsSection />}
          {currentSection === 'evaluation' && <EvaluationSection />}
          {currentSection === 'reinforcement' && <ReinforcementSection />}
          {currentSection === 'recommendations' && <RecommendationsSection />}
          {currentSection === 'analytics' && <AnalyticsSection metrics={systemMetrics} />}
          {currentSection === 'monitoring' && <MonitoringSection metrics={systemMetrics} />}
          {currentSection === 'visualization' && <VisualizationSection />}
          {currentSection === 'integrations' && <IntegrationsSection />}
          {currentSection === 'plugins' && <PluginsSection />}
          {currentSection === 'backup' && <BackupSection />}
          {currentSection === 'audit' && <AuditSection />}
          {currentSection === 'deployment' && <DeploymentSection />}
          {currentSection === 'i18n' && <I18nSection />}
          {currentSection === 'benchmark' && <BenchmarkSection />}
          {currentSection === 'logs' && <LogsSection />}
          {currentSection === 'debugging' && <DebuggingSection />}
          {currentSection === 'documentation' && <DocumentationSection />}
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
function OverviewSection({ user, systemMetrics, notifications }: { user: User | null, systemMetrics: SystemMetrics | null, notifications: Notification[] }) {
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

// Componente de Entrenamiento Interactivo
function TrainingSection({
  exercises,
  currentExercise,
  setCurrentExercise,
  exerciseAnswer,
  setExerciseAnswer,
  isSubmitting,
  setIsSubmitting,
  progress
}: {
  exercises: TrainingExercise[];
  currentExercise: TrainingExercise | null;
  setCurrentExercise: (exercise: TrainingExercise | null) => void;
  exerciseAnswer: string;
  setExerciseAnswer: (answer: string) => void;
  isSubmitting: boolean;
  setIsSubmitting: (submitting: boolean) => void;
  progress: {[key: string]: {completed: number, total: number}};
}) {
  const submitExercise = async () => {
    if (!currentExercise || !exerciseAnswer.trim()) return;

    setIsSubmitting(true);
    try {
      // Enviar respuesta del ejercicio al backend
      const response = await fetch('http://localhost:8002/api/training/submit-exercise', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          exercise_id: currentExercise.id,
          user_answer: exerciseAnswer.trim(),
          branch_name: currentExercise.branch_name
        })
      });

      if (!response.ok) {
        throw new Error('Error al enviar ejercicio');
      }

      const result = await response.json();

      // Mostrar resultado
      if (result.success) {
        console.log('✅ Ejercicio procesado:', result);

        // Mostrar notificación de éxito
        setNotifications(prev => [{
          id: Date.now().toString(),
          type: result.is_correct ? 'success' : 'warning',
          title: result.is_correct ? '¡Ejercicio Completado!' : 'Respuesta Incorrecta',
          message: result.message,
          timestamp: new Date().toISOString(),
          read: false
        }, ...prev]);

        // Si fue correcto y se generó dataset, mostrar mensaje especial
        if (result.is_correct && result.dataset_generated) {
          setTimeout(() => {
            setNotifications(prev => [{
              id: (Date.now() + 1).toString(),
              type: 'info',
              title: '📊 Dataset Generado',
              message: `Tu respuesta correcta en ${result.branch} ha contribuido al entrenamiento de la IA.`,
              timestamp: new Date().toISOString(),
              read: false
            }, ...prev]);
          }, 1000);
        }

        // Actualizar tokens si se otorgaron
        if (result.tokens_awarded > 0) {
          setTotalTokenBalance(prev => prev + result.tokens_awarded);
        }

        // Cerrar modal y limpiar
        setCurrentExercise(null);
        setExerciseAnswer('');
      } else {
        throw new Error(result.error || 'Error desconocido');
      }

    } catch (error) {
      console.error('Error enviando ejercicio:', error);
      setNotifications(prev => [{
        id: Date.now().toString(),
        type: 'error',
        title: 'Error',
        message: 'No se pudo procesar el ejercicio. Inténtalo de nuevo.',
        timestamp: new Date().toISOString(),
        read: false
      }, ...prev]);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Entrenamiento Interactivo</h2>
          <p className="text-gray-400">Completa ejercicios en diferentes ramas para ganar tokens SHEILY</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Total Tokens Ganados</p>
          <p className="text-xl font-bold text-yellow-400">1,250 SHEILY</p>
        </div>
      </div>

      {/* Progreso por ramas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(progress).map(([branch, prog]) => (
          <div key={branch} className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-semibold mb-2">{branch.replace(/_/g, ' ')}</h3>
            <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${(prog.completed / prog.total) * 100}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-400">{prog.completed}/{prog.total} ejercicios completados</p>
          </div>
        ))}
      </div>

      {/* Ejercicio actual */}
      {currentExercise ? (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Ejercicio Actual</h3>
          <div className="mb-4">
            <span className={`px-2 py-1 rounded text-xs ${
              currentExercise.difficulty === 'easy' ? 'bg-green-600' :
              currentExercise.difficulty === 'medium' ? 'bg-yellow-600' : 'bg-red-600'
            }`}>
              {currentExercise.difficulty.toUpperCase()}
            </span>
            <span className="ml-2 text-gray-400">{currentExercise.branch_name}</span>
          </div>
          <p className="text-gray-300 mb-4">{currentExercise.question}</p>
          <textarea
            value={exerciseAnswer}
            onChange={(e) => setExerciseAnswer(e.target.value)}
            placeholder="Escribe tu respuesta aquí..."
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-24"
          />
          <div className="flex space-x-3 mt-4">
            <button
              onClick={submitExercise}
              disabled={isSubmitting || !exerciseAnswer.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-medium transition-colors"
            >
              {isSubmitting ? '⏳ Enviando...' : '📤 Enviar Respuesta'}
            </button>
            <button
              onClick={() => setCurrentExercise(null)}
              className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Ejercicios Disponibles</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {exercises.slice(0, 6).map(exercise => (
              <div key={exercise.id} className="border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    exercise.difficulty === 'easy' ? 'bg-green-600' :
                    exercise.difficulty === 'medium' ? 'bg-yellow-600' : 'bg-red-600'
                  }`}>
                    {exercise.difficulty.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-400">{exercise.score} pts</span>
                </div>
                <h4 className="font-medium mb-2">{exercise.branch_name}</h4>
                <p className="text-sm text-gray-400 mb-3 line-clamp-2">{exercise.question}</p>
                <button
                  onClick={() => setCurrentExercise(exercise)}
                  className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Resolver Ejercicio
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Componente de Tokens SHEILY
function TokensSection({ user, tokens, transactions, totalBalance }: {
  user: User | null;
  tokens: SheilyToken[];
  transactions: SheilyToken[];
  totalBalance: number;
}) {
  const getTokenTypeColor = (type: string) => {
    switch (type) {
      case 'TRAINING': return 'bg-blue-600';
      case 'RESPONSE': return 'bg-green-600';
      case 'INNOVATION': return 'bg-purple-600';
      case 'GOVERNANCE': return 'bg-yellow-600';
      case 'SPECIAL_CONTRIBUTION': return 'bg-red-600';
      case 'LEARNING': return 'bg-indigo-600';
      case 'DOMAIN_EXPERTISE': return 'bg-pink-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Tokens SHEILY</h2>
          <p className="text-gray-400">Economía completa en blockchain Solana</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Balance Total</p>
          <p className="text-3xl font-bold text-yellow-400">{totalBalance.toLocaleString()}</p>
          <p className="text-sm text-gray-400">SHEILY Tokens</p>
        </div>
      </div>

      {/* Estadísticas de tokens */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-2xl mr-3">🎓</span>
            <div>
              <p className="text-sm text-gray-400">Training</p>
              <p className="text-lg font-semibold">
                {tokens.filter(t => t.token_type === 'TRAINING').reduce((sum, t) => sum + t.amount, 0)}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-2xl mr-3">💬</span>
            <div>
              <p className="text-sm text-gray-400">Response</p>
              <p className="text-lg font-semibold">
                {tokens.filter(t => t.token_type === 'RESPONSE').reduce((sum, t) => sum + t.amount, 0)}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-2xl mr-3">🚀</span>
            <div>
              <p className="text-sm text-gray-400">Innovation</p>
              <p className="text-lg font-semibold">
                {tokens.filter(t => t.token_type === 'INNOVATION').reduce((sum, t) => sum + t.amount, 0)}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-2xl mr-3">🏛️</span>
            <div>
              <p className="text-sm text-gray-400">Governance</p>
              <p className="text-lg font-semibold">
                {tokens.filter(t => t.token_type === 'GOVERNANCE').reduce((sum, t) => sum + t.amount, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Transacciones recientes */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Transacciones Recientes</h3>
        <div className="space-y-3">
          {transactions.slice(0, 10).map(transaction => (
            <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className={`px-2 py-1 rounded text-xs ${getTokenTypeColor(transaction.token_type)}`}>
                  {transaction.token_type}
                </span>
                <div>
                  <p className="text-sm font-medium">{transaction.reason}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-semibold ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {transaction.amount > 0 ? '+' : ''}{transaction.amount}
                </p>
                <p className="text-xs text-gray-400">SHEILY</p>
              </div>
            </div>
          ))}
          {transactions.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <p>No hay transacciones recientes</p>
            </div>
          )}
        </div>
      </div>

      {/* Información de staking */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Staking Pools Disponibles</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-700 rounded-lg p-4">
            <h4 className="font-semibold mb-2">Basic Pool</h4>
            <p className="text-2xl font-bold text-green-400 mb-2">5% APY</p>
            <p className="text-sm text-gray-400 mb-3">Lock: 30 días | Min: 10 SHEILY</p>
            <button className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
              Hacer Stake
            </button>
          </div>
          <div className="border border-gray-700 rounded-lg p-4">
            <h4 className="font-semibold mb-2">Advanced Pool</h4>
            <p className="text-2xl font-bold text-yellow-400 mb-2">10% APY</p>
            <p className="text-sm text-gray-400 mb-3">Lock: 90 días | Min: 100 SHEILY</p>
            <button className="w-full bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded-lg font-medium transition-colors">
              Hacer Stake
            </button>
          </div>
          <div className="border border-gray-700 rounded-lg p-4">
            <h4 className="font-semibold mb-2">Expert Pool</h4>
            <p className="text-2xl font-bold text-red-400 mb-2">15% APY</p>
            <p className="text-sm text-gray-400 mb-3">Lock: 180 días | Min: 500 SHEILY</p>
            <button className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium transition-colors">
              Hacer Stake
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Blockchain y Phantom Wallet
function BlockchainSection({ wallet, transactions, setWallet }: {
  wallet: PhantomWallet;
  transactions: BlockchainTransaction[];
  setWallet: (wallet: PhantomWallet) => void;
}) {
  const connectPhantom = async () => {
    try {
      // Aquí iría la lógica real de conexión con Phantom
      console.log('Conectando a Phantom wallet...');
      // Simular conexión exitosa
      setWallet({
        connected: true,
        address: '7xKXtg2CW87ZdZ8QQrN5Pm8KZiHqR8ZAX',
        balance: 1250.50,
        network: 'mainnet-beta'
      });
    } catch (error) {
      console.error('Error conectando wallet:', error);
    }
  };

  const disconnectPhantom = () => {
    setWallet({
      connected: false,
      address: '',
      balance: 0,
      network: 'devnet'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Phantom Wallet Integration</h2>
          <p className="text-gray-400">Conecta tu wallet y gestiona tokens SHEILY en Solana</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Red Actual</p>
          <p className="text-lg font-semibold text-green-400">
            {wallet.network === 'mainnet-beta' ? 'Mainnet' : 'Devnet'}
          </p>
        </div>
      </div>

      {/* Estado de la wallet */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Estado de la Wallet</h3>
        {wallet.connected ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">👻</span>
                <div>
                  <p className="font-medium">Phantom Wallet</p>
                  <p className="text-sm text-gray-400">
                    {wallet.address.slice(0, 8)}...{wallet.address.slice(-8)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-yellow-400">{wallet.balance.toFixed(2)}</p>
                <p className="text-sm text-gray-400">SHEILY</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <button className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
                💸 Enviar Tokens
              </button>
              <button className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
                📥 Recibir Tokens
              </button>
              <button
                onClick={disconnectPhantom}
                className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                🔌 Desconectar
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <span className="text-6xl mb-4 block">👻</span>
            <h4 className="text-lg font-semibold mb-2">Wallet No Conectada</h4>
            <p className="text-gray-400 mb-6">Conecta tu wallet Phantom para gestionar tus tokens SHEILY</p>
            <button
              onClick={connectPhantom}
              className="bg-purple-600 hover:bg-purple-700 px-8 py-3 rounded-lg font-medium transition-colors"
            >
              🔗 Conectar Phantom
            </button>
          </div>
        )}
      </div>

      {/* Transacciones blockchain */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Transacciones en Blockchain</h3>
        <div className="space-y-3">
          {transactions.slice(0, 8).map(tx => (
            <div key={tx.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className={`px-2 py-1 rounded text-xs ${
                  tx.type === 'mint' ? 'bg-green-600' :
                  tx.type === 'transfer' ? 'bg-blue-600' :
                  tx.type === 'burn' ? 'bg-red-600' : 'bg-yellow-600'
                }`}>
                  {tx.type.toUpperCase()}
                </span>
                <div>
                  <p className="text-sm font-medium">
                    {tx.from_address.slice(0, 6)}... → {tx.to_address.slice(0, 6)}...
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(tx.timestamp).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-semibold ${
                  tx.type === 'mint' ? 'text-green-400' :
                  tx.type === 'transfer' ? 'text-blue-400' :
                  tx.type === 'burn' ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {tx.amount} SHEILY
                </p>
                <span className={`px-2 py-1 rounded text-xs ${
                  tx.status === 'confirmed' ? 'bg-green-600' :
                  tx.status === 'pending' ? 'bg-yellow-600' : 'bg-red-600'
                }`}>
                  {tx.status === 'confirmed' ? '✅' :
                   tx.status === 'pending' ? '⏳' : '❌'}
                </span>
              </div>
            </div>
          ))}
          {transactions.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <p>No hay transacciones blockchain</p>
            </div>
          )}
        </div>
      </div>

      {/* Información de red */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">99.9%</p>
          <p className="text-sm text-gray-400">Uptime Red</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">1.2s</p>
          <p className="text-sm text-gray-400">Tiempo Confirmación</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">0.000005</p>
          <p className="text-sm text-gray-400">Fee Promedio (SOL)</p>
        </div>
      </div>
    </div>
  );
}

// Componente de Gobernanza DAO
function GovernanceSection({ proposals, userTokens }: { proposals: GovernanceProposal[]; userTokens: number }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Gobernanza DAO</h2>
          <p className="text-gray-400">Participa en la gobernanza con tus tokens SHEILY</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Poder de Voto</p>
          <p className="text-xl font-bold text-yellow-400">{userTokens.toLocaleString()}</p>
          <p className="text-sm text-gray-400">Tokens SHEILY</p>
        </div>
      </div>

      {/* Estadísticas de gobernanza */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">{proposals.filter(p => p.status === 'active').length}</p>
          <p className="text-sm text-gray-400">Propuestas Activas</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">{proposals.filter(p => p.status === 'passed').length}</p>
          <p className="text-sm text-gray-400">Propuestas Aprobadas</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-red-400">{proposals.filter(p => p.status === 'rejected').length}</p>
          <p className="text-sm text-gray-400">Propuestas Rechazadas</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">{proposals.filter(p => p.status === 'executed').length}</p>
          <p className="text-sm text-gray-400">Propuestas Ejecutadas</p>
        </div>
      </div>

      {/* Crear nueva propuesta */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Crear Nueva Propuesta</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Título de la propuesta"
            className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="feature">Nueva Funcionalidad</option>
            <option value="parameter">Cambio de Parámetros</option>
            <option value="funding">Asignación de Fondos</option>
            <option value="governance">Cambio de Gobernanza</option>
          </select>
        </div>
        <textarea
          placeholder="Descripción detallada de la propuesta..."
          rows={4}
          className="w-full mt-4 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div className="flex justify-end mt-4">
          <button className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium transition-colors">
            📝 Crear Propuesta
          </button>
        </div>
      </div>

      {/* Propuestas activas */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Propuestas Activas</h3>
        <div className="space-y-4">
          {proposals.filter(p => p.status === 'active').map(proposal => (
            <div key={proposal.id} className="border border-gray-700 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-semibold mb-1">{proposal.title}</h4>
                  <p className="text-sm text-gray-400 mb-2">{proposal.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-400">
                    <span>👤 {proposal.proposer}</span>
                    <span>⏰ {new Date(proposal.deadline).toLocaleDateString()}</span>
                  </div>
                </div>
                <span className="px-3 py-1 bg-blue-600 text-white text-xs rounded-full">
                  {proposal.status.toUpperCase()}
                </span>
              </div>

              {/* Barra de progreso de votos */}
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-green-400">👍 {proposal.votes_for}</span>
                  <span className="text-red-400">👎 {proposal.votes_against}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${(proposal.votes_for / (proposal.votes_for + proposal.votes_against)) * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="flex space-x-2">
                <button className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
                  👍 Votar Sí
                </button>
                <button className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-medium transition-colors">
                  👎 Votar No
                </button>
              </div>
            </div>
          ))}
          {proposals.filter(p => p.status === 'active').length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <p>No hay propuestas activas actualmente</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Componente de Analytics
function AnalyticsSection({ metrics }: { metrics: SystemMetrics | null }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Analytics y Estadísticas</h2>
          <p className="text-gray-400">Análisis detallado del rendimiento del sistema</p>
        </div>
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Uso de Recursos</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">CPU</span>
                <span className="text-sm">{metrics?.cpu_usage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${metrics?.cpu_usage || 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">Memoria</span>
                <span className="text-sm">{metrics?.memory_usage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${metrics?.memory_usage || 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">Disco</span>
                <span className="text-sm">{metrics?.disk_usage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-yellow-600 h-2 rounded-full"
                  style={{ width: `${metrics?.disk_usage || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Actividad del Sistema</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <p className="text-2xl font-bold text-blue-400">{metrics?.active_connections || 0}</p>
              <p className="text-sm text-gray-400">Conexiones Activas</p>
            </div>
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <p className="text-2xl font-bold text-green-400">{metrics?.total_requests || 0}</p>
              <p className="text-sm text-gray-400">Total Requests</p>
            </div>
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <p className="text-2xl font-bold text-red-400">{(metrics?.error_rate || 0).toFixed(2)}%</p>
              <p className="text-sm text-gray-400">Tasa de Error</p>
            </div>
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <p className="text-2xl font-bold text-purple-400">{metrics?.uptime || 'N/A'}</p>
              <p className="text-sm text-gray-400">Uptime</p>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos históricos (simulados) */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Tendencias de Uso (Últimas 24h)</h3>
        <div className="h-64 flex items-end justify-between space-x-1">
          {Array.from({ length: 24 }, (_, i) => (
            <div key={i} className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t" style={{
              height: `${Math.random() * 60 + 20}%`,
              minHeight: '20%'
            }}></div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-400">
          <span>00:00</span>
          <span>12:00</span>
          <span>23:59</span>
        </div>
      </div>
    </div>
  );
}

// Componente de Monitoreo
function MonitoringSection({ metrics }: { metrics: SystemMetrics | null }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Monitoreo del Sistema</h2>
          <p className="text-gray-400">Estado en tiempo real de todos los componentes</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-sm text-green-400">Sistema Operativo</span>
        </div>
      </div>

      {/* Estado de servicios */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">API Server</span>
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          </div>
          <p className="text-xs text-gray-400">Puerto 8002</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">LLM Server</span>
            <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
          </div>
          <p className="text-xs text-gray-400">Puerto 8001</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">Frontend</span>
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          </div>
          <p className="text-xs text-gray-400">Puerto 3000</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">Base de Datos</span>
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          </div>
          <p className="text-xs text-gray-400">SQLite</p>
        </div>
      </div>

      {/* Logs del sistema */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Logs del Sistema</h3>
        <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-64 overflow-y-auto">
          <div className="space-y-1">
            <div className="text-green-400">[INFO] API Server started on port 8002</div>
            <div className="text-blue-400">[INFO] Database connection established</div>
            <div className="text-yellow-400">[WARN] LLM Server not available, using fallback</div>
            <div className="text-green-400">[INFO] Frontend compiled successfully</div>
            <div className="text-blue-400">[INFO] 35 branches loaded successfully</div>
            <div className="text-green-400">[INFO] Authentication system initialized</div>
            <div className="text-blue-400">[INFO] Token system ready</div>
            <div className="text-green-400">[INFO] All services operational</div>
          </div>
        </div>
      </div>

      {/* Alertas activas */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Alertas Activas</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-yellow-400">⚠️</span>
              <div>
                <p className="font-medium">LLM Server No Disponible</p>
                <p className="text-sm text-gray-400">Usando modo fallback</p>
              </div>
            </div>
            <span className="text-xs text-yellow-400">Hace 2h</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Plugins
function PluginsSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Plugins</h2>
          <p className="text-gray-400">Gestiona extensiones y plugins del sistema</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
          ➕ Instalar Plugin
        </button>
      </div>

      {/* Plugins instalados */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Plugin de Logging</h3>
            <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Activo</span>
          </div>
          <p className="text-sm text-gray-400 mb-4">Sistema avanzado de logging y auditoría</p>
          <div className="flex space-x-2">
            <button className="flex-1 bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
              Configurar
            </button>
            <button className="flex-1 bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition-colors">
              Desactivar
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Plugin de Backup</h3>
            <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Activo</span>
          </div>
          <p className="text-sm text-gray-400 mb-4">Copias de seguridad automáticas</p>
          <div className="flex space-x-2">
            <button className="flex-1 bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
              Configurar
            </button>
            <button className="flex-1 bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition-colors">
              Desactivar
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Plugin de Analytics</h3>
            <span className="px-2 py-1 bg-yellow-600 text-white text-xs rounded-full">Inactivo</span>
          </div>
          <p className="text-sm text-gray-400 mb-4">Análisis avanzado de datos</p>
          <div className="flex space-x-2">
            <button className="flex-1 bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors">
              Activar
            </button>
            <button className="flex-1 bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
              Configurar
            </button>
          </div>
        </div>
      </div>

      {/* Marketplace de plugins */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Plugin Marketplace</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
            <h4 className="font-semibold mb-2">Plugin de Notificaciones Avanzadas</h4>
            <p className="text-sm text-gray-400 mb-3">Integración con Slack, Discord y más plataformas</p>
            <button className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
              Instalar - Gratis
            </button>
          </div>
          <div className="border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
            <h4 className="font-semibold mb-2">Plugin de Machine Learning</h4>
            <p className="text-sm text-gray-400 mb-3">Modelos ML personalizados y auto-entrenamiento</p>
            <button className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
              Instalar - $9.99/mes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Backup
function BackupSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Backup</h2>
          <p className="text-gray-400">Gestiona copias de seguridad y recuperación</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
          💾 Crear Backup
        </button>
      </div>

      {/* Estado del último backup */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Último Backup</h3>
        <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
          <div>
            <p className="font-medium">Backup Completo del Sistema</p>
            <p className="text-sm text-gray-400">Creado: Hace 2 horas | Tamaño: 1.2 GB</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Exitoso</span>
            <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
              Descargar
            </button>
          </div>
        </div>
      </div>

      {/* Configuración de backup */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Configuración Automática</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Frecuencia de Backup</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="daily">Diario</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensual</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Retención (días)</label>
            <input
              type="number"
              defaultValue="30"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="mt-4">
          <label className="flex items-center">
            <input type="checkbox" defaultChecked className="mr-2" />
            <span className="text-sm">Incluir datos de usuario en backups</span>
          </label>
        </div>
        <div className="flex justify-end mt-4">
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
            💾 Guardar Configuración
          </button>
        </div>
      </div>

      {/* Historial de backups */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Historial de Backups</h3>
        <div className="space-y-3">
          {[
            { name: 'backup_2024-01-15.zip', size: '1.2 GB', status: 'success', date: '2024-01-15 14:30' },
            { name: 'backup_2024-01-14.zip', size: '1.1 GB', status: 'success', date: '2024-01-14 14:30' },
            { name: 'backup_2024-01-13.zip', size: '1.3 GB', status: 'failed', date: '2024-01-13 14:30' },
          ].map((backup, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
              <div>
                <p className="font-medium">{backup.name}</p>
                <p className="text-sm text-gray-400">{backup.date} | {backup.size}</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  backup.status === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                }`}>
                  {backup.status === 'success' ? '✅' : '❌'}
                </span>
                <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
                  Descargar
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors">
                  Restaurar
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Componente de Memoria Inteligente
function MemorySection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Memoria Inteligente</h2>
          <p className="text-gray-400">Memoria episódica, semántica y a corto plazo con RAG</p>
        </div>
      </div>

      {/* Estadísticas de memoria */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">1.2M</p>
          <p className="text-sm text-gray-400">Embeddings Almacenados</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">89.7%</p>
          <p className="text-sm text-gray-400">Precisión Recuperación</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">256</p>
          <p className="text-sm text-gray-400">Tokens Contexto</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">47ms</p>
          <p className="text-sm text-gray-400">Tiempo Búsqueda</p>
        </div>
      </div>

      {/* Tipos de memoria */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">🧠 Memoria Episódica</h3>
          <p className="text-sm text-gray-400 mb-4">Recuerdos específicos de interacciones y eventos</p>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Conversaciones guardadas</span>
              <span className="text-blue-400">1,247</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Eventos importantes</span>
              <span className="text-blue-400">89</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Patrones aprendidos</span>
              <span className="text-blue-400">156</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">📚 Memoria Semántica</h3>
          <p className="text-sm text-gray-400 mb-4">Conocimiento factual y significado de conceptos</p>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Conceptos indexados</span>
              <span className="text-green-400">5,432</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Relaciones semánticas</span>
              <span className="text-green-400">12,847</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Grafos de conocimiento</span>
              <span className="text-green-400">23</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">⚡ Memoria a Corto Plazo</h3>
          <p className="text-sm text-gray-400 mb-4">Información temporal para contexto inmediato</p>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Tokens activos</span>
              <span className="text-purple-400">2,147</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>TTL promedio</span>
              <span className="text-purple-400">45min</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Compresión ratio</span>
              <span className="text-purple-400">73%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sistema RAG */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔍 Sistema RAG (Retrieval-Augmented Generation)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Configuración FAISS</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Dimensión embeddings</span>
                <span className="text-blue-400">768</span>
              </div>
              <div className="flex justify-between">
                <span>Índice tipo</span>
                <span className="text-blue-400">IVF1024,PQ32</span>
              </div>
              <div className="flex justify-between">
                <span>Distancia</span>
                <span className="text-blue-400">Cosinus</span>
              </div>
              <div className="flex justify-between">
                <span>Umbral similitud</span>
                <span className="text-blue-400">0.85</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Estadísticas de Recuperación</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Consultas/segundo</span>
                <span className="text-green-400">47.2</span>
              </div>
              <div className="flex justify-between">
                <span>Top-K resultados</span>
                <span className="text-green-400">5</span>
              </div>
              <div className="flex justify-between">
                <span>Re-rank con BERT</span>
                <span className="text-green-400">Activado</span>
              </div>
              <div className="flex justify-between">
                <span>Cache hits</span>
                <span className="text-green-400">94.7%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Plasticidad Neural Simulada */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🧬 Plasticidad Neural Simulada</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-xl font-bold text-red-400">Hebbiana</p>
            <p className="text-sm text-gray-400">Conexiones que se activan juntas se fortalecen</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-xl font-bold text-blue-400">Spike-Timing</p>
            <p className="text-sm text-gray-400">Dependiente del tiempo entre spikes</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-xl font-bold text-green-400">Homeostática</p>
            <p className="text-sm text-gray-400">Regulación de excitabilidad global</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Embeddings y Búsqueda Semántica
function EmbeddingsSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Embeddings y Búsqueda Semántica</h2>
          <p className="text-gray-400">Sistema avanzado de vectorización y recuperación semántica</p>
        </div>
      </div>

      {/* Motor de Búsqueda Semántica */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔍 Motor de Búsqueda Semántica</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Configuración FAISS</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Dimensión vectorial</span>
                <span className="text-blue-400">768</span>
              </div>
              <div className="flex justify-between">
                <span>Índice cuantizado</span>
                <span className="text-blue-400">PQ32x8</span>
              </div>
              <div className="flex justify-between">
                <span>Métrica distancia</span>
                <span className="text-blue-400">IP (Inner Product)</span>
              </div>
              <div className="flex justify-between">
                <span>Tamaño lote</span>
                <span className="text-blue-400">128</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Performance Metrics</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Recall@10</span>
                <span className="text-green-400">94.7%</span>
              </div>
              <div className="flex justify-between">
                <span>Query latency</span>
                <span className="text-green-400">23ms</span>
              </div>
              <div className="flex justify-between">
                <span>Throughput</span>
                <span className="text-green-400">847 qps</span>
              </div>
              <div className="flex justify-between">
                <span>Memory usage</span>
                <span className="text-green-400">2.3 GB</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Clustering Automático */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Clustering Automático de Contenido</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-purple-400">47</p>
            <p className="text-sm text-gray-400">Clusters Detectados</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-blue-400">0.78</p>
            <p className="text-sm text-gray-400">Silhouette Score</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-green-400">K-means++</p>
            <p className="text-sm text-gray-400">Algoritmo Usado</p>
          </div>
        </div>
      </div>

      {/* Similitud Semántica */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔗 Análisis de Similitud Semántica</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Texto de consulta</label>
            <input
              type="text"
              placeholder="Ingresa un texto para buscar similitudes..."
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium transition-colors">
            🔍 Buscar Similitudes
          </button>
        </div>

        {/* Resultados de ejemplo */}
        <div className="mt-6 space-y-3">
          {[
            { text: "Procesamiento de lenguaje natural avanzado", score: 0.94 },
            { text: "Modelos de transformers para NLP", score: 0.87 },
            { text: "Embeddings contextuales con BERT", score: 0.82 },
            { text: "Técnicas de fine-tuning para LLMs", score: 0.79 },
            { text: "Vectorización semántica de texto", score: 0.76 }
          ].map((result, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
              <span className="text-sm">{result.text}</span>
              <span className="text-sm text-green-400 font-mono">{result.score}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Componente de Evaluación de IA
function EvaluationSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Evaluación de Calidad de IA</h2>
          <p className="text-gray-400">Métricas de coherencia, diversidad y factualidad</p>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">94.7%</p>
          <p className="text-sm text-gray-400">Coherencia</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">87.3%</p>
          <p className="text-sm text-gray-400">Diversidad</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">91.2%</p>
          <p className="text-sm text-gray-400">Factualidad</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">2.1</p>
          <p className="text-sm text-gray-400">Toxicidad</p>
        </div>
      </div>

      {/* Evaluación de respuestas */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔬 Evaluación Automática de Respuestas</h3>
        <div className="space-y-4">
          <textarea
            placeholder="Ingresa una respuesta de IA para evaluar..."
            rows={4}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium transition-colors">
            📊 Evaluar Respuesta
          </button>
        </div>
      </div>

      {/* Benchmarks de rendimiento */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">⚡ Benchmarks de Rendimiento</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2">Modelo</th>
                <th className="text-center py-2">MMLU</th>
                <th className="text-center py-2">TruthfulQA</th>
                <th className="text-center py-2">GSM8K</th>
                <th className="text-center py-2">Tiempo Inferencia</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              <tr>
                <td className="py-2">Llama-3.2-3B (Base)</td>
                <td className="text-center py-2">67.2%</td>
                <td className="text-center py-2">54.3%</td>
                <td className="text-center py-2">23.1%</td>
                <td className="text-center py-2">1.2s</td>
              </tr>
              <tr>
                <td className="py-2">Llama-3.2-3B + LoRA</td>
                <td className="text-center py-2">71.8%</td>
                <td className="text-center py-2">58.7%</td>
                <td className="text-center py-2">28.4%</td>
                <td className="text-center py-2">1.1s</td>
              </tr>
              <tr>
                <td className="py-2">Phi-3-mini-4k</td>
                <td className="text-center py-2">69.4%</td>
                <td className="text-center py-2">61.2%</td>
                <td className="text-center py-2">45.7%</td>
                <td className="text-center py-2">0.8s</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Componente de Aprendizaje por Refuerzo
function ReinforcementSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Aprendizaje por Refuerzo</h2>
          <p className="text-gray-400">Optimización continua basada en feedback y recompensas</p>
        </div>
      </div>

      {/* Agente de Aprendizaje Adaptativo */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🎯 Agente de Aprendizaje Adaptativo</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-green-400">PPO</p>
            <p className="text-sm text-gray-400">Proximal Policy Optimization</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-blue-400">A2C</p>
            <p className="text-sm text-gray-400">Advantage Actor-Critic</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-purple-400">DDPG</p>
            <p className="text-sm text-gray-400">Deep Deterministic Policy Gradient</p>
          </div>
        </div>
      </div>

      {/* Exploración vs Explotación */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔄 Balance Exploración vs Explotación</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">ε-Greedy Strategy</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>ε inicial</span>
                <span className="text-blue-400">1.0</span>
              </div>
              <div className="flex justify-between">
                <span>ε final</span>
                <span className="text-blue-400">0.01</span>
              </div>
              <div className="flex justify-between">
                <span>Decay rate</span>
                <span className="text-blue-400">0.995</span>
              </div>
              <div className="flex justify-between">
                <span>ε actual</span>
                <span className="text-blue-400">0.087</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Softmax Exploration</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Temperature</span>
                <span className="text-green-400">0.7</span>
              </div>
              <div className="flex justify-between">
                <span>Annealing</span>
                <span className="text-green-400">0.999</span>
              </div>
              <div className="flex justify-between">
                <span>Entropy bonus</span>
                <span className="text-green-400">0.01</span>
              </div>
              <div className="flex justify-between">
                <span>KL divergence</span>
                <span className="text-green-400">0.02</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas de RL */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-red-400">1,247</p>
          <p className="text-sm text-gray-400">Episodios Completados</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">847.3</p>
          <p className="text-sm text-gray-400">Recompensa Promedio</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">23.7</p>
          <p className="text-sm text-gray-400">Longitud Episodio</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">94.2%</p>
          <p className="text-sm text-gray-400">Tasa de Convergencia</p>
        </div>
      </div>
    </div>
  );
}

// Componente de Recomendaciones Personalizadas
function RecommendationsSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Recomendaciones</h2>
          <p className="text-gray-400">Recomendaciones personalizadas basadas en comportamiento</p>
        </div>
      </div>

      {/* Motor de Recomendaciones */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🎯 Motor de Recomendaciones ML</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium mb-3">Collaborative Filtering</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Usuarios similares</span>
                <span className="text-blue-400">1,247</span>
              </div>
              <div className="flex justify-between">
                <span>Matrix factorization</span>
                <span className="text-blue-400">SVD++</span>
              </div>
              <div className="flex justify-between">
                <span>MAE</span>
                <span className="text-blue-400">0.023</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Content-Based</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Features extraídas</span>
                <span className="text-green-400">847</span>
              </div>
              <div className="flex justify-between">
                <span>TF-IDF weighting</span>
                <span className="text-green-400">Activado</span>
              </div>
              <div className="flex justify-between">
                <span>Cosine similarity</span>
                <span className="text-green-400">0.89</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Hybrid Approach</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Ensemble weight</span>
                <span className="text-purple-400">0.7/0.3</span>
              </div>
              <div className="flex justify-between">
                <span>A/B testing</span>
                <span className="text-purple-400">94.2% win</span>
              </div>
              <div className="flex justify-between">
                <span>Cache hits</span>
                <span className="text-purple-400">87.3%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recomendaciones actuales */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">💡 Recomendaciones Personalizadas</h3>
        <div className="space-y-4">
          <div className="border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Ejercicios de Matemáticas Avanzadas</span>
              <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">Recomendado</span>
            </div>
            <p className="text-sm text-gray-400 mb-3">Basado en tu progreso en álgebra lineal y cálculo</p>
            <div className="flex items-center space-x-3 text-sm">
              <span>📈 Confianza: 94%</span>
              <span>🎯 Dificultad: Alta</span>
              <span>⏱️ Tiempo estimado: 45 min</span>
            </div>
          </div>

          <div className="border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Rama de Neurociencia</span>
              <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Descubre</span>
            </div>
            <p className="text-sm text-gray-400 mb-3">Usuarios con intereses similares han explorado esta rama</p>
            <div className="flex items-center space-x-3 text-sm">
              <span>👥 Popularidad: 89%</span>
              <span>🔗 Similitud: 0.87</span>
              <span>📚 Contenido: 247 ejercicios</span>
            </div>
          </div>

          <div className="border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Sesión de práctica intensiva</span>
              <span className="px-2 py-1 bg-purple-600 text-white text-xs rounded-full">Personalizado</span>
            </div>
            <p className="text-sm text-gray-400 mb-3">Optimizado para tu patrón de aprendizaje matutino</p>
            <div className="flex items-center space-x-3 text-sm">
              <span>🕐 Horario óptimo: 9:00 AM</span>
              <span>🎯 Foco: Programación</span>
              <span>🏆 Tokens estimados: 150</span>
            </div>
          </div>
        </div>
      </div>

      {/* Feedback loops */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔄 Loops de Feedback</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Sistema de Ratings</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Recomendaciones puntuadas</span>
                <span className="text-blue-400">12,347</span>
              </div>
              <div className="flex justify-between">
                <span>Rating promedio</span>
                <span className="text-blue-400">4.7/5.0</span>
              </div>
              <div className="flex justify-between">
                <span>CTR de recomendaciones</span>
                <span className="text-blue-400">73.2%</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Mejora Continua</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Modelo re-entrenado</span>
                <span className="text-green-400">47 veces</span>
              </div>
              <div className="flex justify-between">
                <span>Mejora precisión</span>
                <span className="text-green-400">+23.7%</span>
              </div>
              <div className="flex justify-between">
                <span>Datos nuevos/día</span>
                <span className="text-green-400">1,247</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Visualización de Datos
function VisualizationSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Visualización de Datos</h2>
          <p className="text-gray-400">Dashboards interactivos con Plotly y análisis avanzado</p>
        </div>
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">📈 Rendimiento por Rama</h3>
          <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
            <span className="text-gray-400">Gráfico de barras interactivo</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">🧠 Embeddings 3D</h3>
          <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
            <span className="text-gray-400">Visualización 3D de embeddings</span>
          </div>
        </div>
      </div>

      {/* Mapas de calor */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔥 Mapas de Calor de Actividad</h3>
        <div className="h-48 bg-gray-700 rounded-lg flex items-center justify-center">
          <span className="text-gray-400">Heatmap de uso del sistema</span>
        </div>
      </div>

      {/* Reportes automáticos */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Reportes Automáticos</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <p className="font-medium">Reporte Semanal de Rendimiento</p>
              <p className="text-sm text-gray-400">Generado automáticamente cada lunes</p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors">
              Descargar PDF
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <p className="font-medium">Análisis de Tendencias Mensual</p>
              <p className="text-sm text-gray-400">Estadísticas completas del mes</p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors">
              Descargar PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Integraciones
function IntegrationsSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Integraciones Externas</h2>
          <p className="text-gray-400">Conecta Sheily AI con tus herramientas favoritas</p>
        </div>
      </div>

      {/* Webhooks */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔗 Webhooks y APIs</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📡</span>
              <div>
                <p className="font-medium">Webhook de Eventos</p>
                <p className="text-sm text-gray-400">Notificaciones en tiempo real</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Activo</span>
              <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
                Configurar
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔄</span>
              <div>
                <p className="font-medium">API REST Externa</p>
                <p className="text-sm text-gray-400">Integración con sistemas externos</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">Configurado</span>
              <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
                Probar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Integraciones de plataformas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <span className="text-4xl mb-3 block">💬</span>
          <h4 className="font-semibold mb-2">Slack</h4>
          <p className="text-sm text-gray-400 mb-4">Notificaciones y comandos</p>
          <button className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Conectar
          </button>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <span className="text-4xl mb-3 block">🎮</span>
          <h4 className="font-semibold mb-2">Discord</h4>
          <p className="text-sm text-gray-400 mb-4">Bot integrado y canales</p>
          <button className="w-full bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Conectar
          </button>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <span className="text-4xl mb-3 block">☁️</span>
          <h4 className="font-semibold mb-2">Cloud Services</h4>
          <p className="text-sm text-gray-400 mb-4">AWS, GCP, Azure</p>
          <button className="w-full bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Configurar
          </button>
        </div>
      </div>
    </div>
  );
}

// Componente de Auditoría
function AuditSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Auditoría</h2>
          <p className="text-gray-400">Registro completo de acciones y cumplimiento normativo</p>
        </div>
      </div>

      {/* Logs de auditoría */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📝 Logs de Auditoría</h3>
        <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-64 overflow-y-auto">
          <div className="space-y-1">
            <div className="text-green-400">[INFO] Usuario admin inició sesión - IP: 192.168.1.100</div>
            <div className="text-blue-400">[INFO] Dataset generado para rama Matemáticas - Usuario: user123</div>
            <div className="text-yellow-400">[WARN] Intento de acceso no autorizado - IP: 10.0.0.50</div>
            <div className="text-green-400">[INFO] Entrenamiento LoRA completado - Modelo: Llama-3.2-Math</div>
            <div className="text-blue-400">[INFO] Tokens SHEILY minteados - Cantidad: 50 - Usuario: user456</div>
            <div className="text-green-400">[INFO] Backup automático completado - Tamaño: 2.3GB</div>
          </div>
        </div>
      </div>

      {/* Cumplimiento normativo */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">⚖️ Cumplimiento Normativo</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-green-400">✅</p>
            <p className="text-sm text-gray-400">GDPR Compliant</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-green-400">✅</p>
            <p className="text-sm text-gray-400">SOX Compliant</p>
          </div>
          <div className="text-center p-4 bg-gray-700 rounded-lg">
            <p className="text-2xl font-bold text-green-400">✅</p>
            <p className="text-sm text-gray-400">ISO 27001</p>
          </div>
        </div>
      </div>

      {/* Reportes de auditoría */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Reportes de Auditoría</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <p className="font-medium">Reporte Mensual de Seguridad</p>
              <p className="text-sm text-gray-400">Análisis completo de accesos y eventos</p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors">
              Generar
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <p className="font-medium">Auditoría de Datos Personales</p>
              <p className="text-sm text-gray-400">Cumplimiento GDPR y privacidad</p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors">
              Generar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Despliegue CI/CD
function DeploymentSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Despliegue CI/CD</h2>
          <p className="text-gray-400">Pipelines automatizados y despliegue continuo</p>
        </div>
      </div>

      {/* Estado de pipelines */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-white font-bold">✓</span>
          </div>
          <p className="font-semibold mb-1">Desarrollo</p>
          <p className="text-sm text-gray-400">Pipeline activo</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-white font-bold">⟳</span>
          </div>
          <p className="font-semibold mb-1">Staging</p>
          <p className="text-sm text-gray-400">Desplegando...</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-white font-bold">✓</span>
          </div>
          <p className="font-semibold mb-1">Producción</p>
          <p className="text-sm text-gray-400">Estable</p>
        </div>
      </div>

      {/* Últimos despliegues */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🚀 Últimos Despliegues</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <p className="font-medium">v3.1.0 - Nueva UI del Dashboard</p>
              <p className="text-sm text-gray-400">Desplegado hace 2 horas | Commit: abc123</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Éxito</span>
              <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
                Rollback
              </button>
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div>
              <p className="font-medium">v3.0.9 - Sistema LoRA Mejorado</p>
              <p className="text-sm text-gray-400">Desplegado hace 1 día | Commit: def456</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Éxito</span>
              <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm transition-colors">
                Rollback
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Configuración de entornos */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">⚙️ Configuración Multi-entorno</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-700 rounded-lg p-4">
            <h4 className="font-semibold mb-2 text-green-400">Desarrollo</h4>
            <div className="space-y-1 text-sm text-gray-400">
              <p>Debug: Activado</p>
              <p>Cache: Desactivado</p>
              <p>SSL: No requerido</p>
            </div>
          </div>
          <div className="border border-gray-700 rounded-lg p-4">
            <h4 className="font-semibold mb-2 text-blue-400">Staging</h4>
            <div className="space-y-1 text-sm text-gray-400">
              <p>Debug: Limitado</p>
              <p>Cache: Activado</p>
              <p>SSL: Requerido</p>
            </div>
          </div>
          <div className="border border-gray-700 rounded-lg p-4">
            <h4 className="font-semibold mb-2 text-red-400">Producción</h4>
            <div className="space-y-1 text-sm text-gray-400">
              <p>Debug: Desactivado</p>
              <p>Cache: Optimizado</p>
              <p>SSL: Obligatorio</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Internacionalización
function I18nSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Internacionalización</h2>
          <p className="text-gray-400">Soporte multiidioma completo para usuarios globales</p>
        </div>
      </div>

      {/* Idiomas soportados */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🌍 Idiomas Soportados</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { code: 'es', name: 'Español', flag: '🇪🇸', completion: '100%' },
            { code: 'en', name: 'English', flag: '🇺🇸', completion: '95%' },
            { code: 'fr', name: 'Français', flag: '🇫🇷', completion: '87%' },
            { code: 'de', name: 'Deutsch', flag: '🇩🇪', completion: '82%' },
            { code: 'it', name: 'Italiano', flag: '🇮🇹', completion: '79%' },
            { code: 'pt', name: 'Português', flag: '🇵🇹', completion: '76%' },
            { code: 'zh', name: '中文', flag: '🇨🇳', completion: '73%' },
            { code: 'ja', name: '日本語', flag: '🇯🇵', completion: '71%' }
          ].map(lang => (
            <div key={lang.code} className="text-center p-3 bg-gray-700 rounded-lg">
              <span className="text-2xl mb-2 block">{lang.flag}</span>
              <p className="font-medium text-sm">{lang.name}</p>
              <p className="text-xs text-gray-400">{lang.completion}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Traducción automática */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔄 Traducción Automática</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Contenido Traducido</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Ejercicios</span>
                <span className="text-blue-400">12,347</span>
              </div>
              <div className="flex justify-between">
                <span>Interfaces</span>
                <span className="text-blue-400">8,921</span>
              </div>
              <div className="flex justify-between">
                <span>Documentación</span>
                <span className="text-blue-400">3,456</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Calidad de Traducción</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>BLEU Score</span>
                <span className="text-green-400">0.87</span>
              </div>
              <div className="flex justify-between">
                <span>Precisión</span>
                <span className="text-green-400">94.2%</span>
              </div>
              <div className="flex justify-between">
                <span>Cobertura</span>
                <span className="text-green-400">89.7%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Configuración regional */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">⚙️ Configuración Regional</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Idioma Principal</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="es">Español</option>
              <option value="en">English</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Zona Horaria</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="Europe/Madrid">Europe/Madrid (CET)</option>
              <option value="America/New_York">America/New_York (EST)</option>
              <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Formato de Fecha</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Benchmarks
function BenchmarkSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Benchmarks y Performance</h2>
          <p className="text-gray-400">Evaluación continua del rendimiento del sistema</p>
        </div>
      </div>

      {/* Benchmarks principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">1.2s</p>
          <p className="text-sm text-gray-400">Tiempo Respuesta API</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">847</p>
          <p className="text-sm text-gray-400">QPS Máximo</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">99.9%</p>
          <p className="text-sm text-gray-400">Disponibilidad</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">23ms</p>
          <p className="text-sm text-gray-400">Latencia IA</p>
        </div>
      </div>

      {/* Gráfico de rendimiento */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📈 Tendencia de Performance</h3>
        <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
          <span className="text-gray-400">Gráfico de rendimiento histórico</span>
        </div>
      </div>

      {/* Benchmarks por componente */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔧 Benchmarks por Componente</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2">Componente</th>
                <th className="text-center py-2">Throughput</th>
                <th className="text-center py-2">Latencia</th>
                <th className="text-center py-2">CPU</th>
                <th className="text-center py-2">Memoria</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              <tr>
                <td className="py-2">API Server</td>
                <td className="text-center py-2">847 req/s</td>
                <td className="text-center py-2">23ms</td>
                <td className="text-center py-2">12%</td>
                <td className="text-center py-2">1.2GB</td>
              </tr>
              <tr>
                <td className="py-2">LLM Inference</td>
                <td className="text-center py-2">47 tokens/s</td>
                <td className="text-center py-2">45ms</td>
                <td className="text-center py-2">78%</td>
                <td className="text-center py-2">4.7GB</td>
              </tr>
              <tr>
                <td className="py-2">Vector Search</td>
                <td className="text-center py-2">1,247 q/s</td>
                <td className="text-center py-2">8ms</td>
                <td className="text-center py-2">5%</td>
                <td className="text-center py-2">2.1GB</td>
              </tr>
              <tr>
                <td className="py-2">Database</td>
                <td className="text-center py-2">3,456 q/s</td>
                <td className="text-center py-2">12ms</td>
                <td className="text-center py-2">15%</td>
                <td className="text-center py-2">3.2GB</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Componente de Sistema de Logs
function LogsSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sistema de Logs</h2>
          <p className="text-gray-400">Logs centralizados con rotación automática y búsqueda avanzada</p>
        </div>
      </div>

      {/* Filtros de logs */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔍 Filtros de Búsqueda</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Todos los niveles</option>
            <option value="ERROR">ERROR</option>
            <option value="WARN">WARN</option>
            <option value="INFO">INFO</option>
            <option value="DEBUG">DEBUG</option>
          </select>
          <select className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Todos los componentes</option>
            <option value="api">API Server</option>
            <option value="llm">LLM Server</option>
            <option value="db">Database</option>
            <option value="auth">Authentication</option>
          </select>
          <input
            type="text"
            placeholder="Buscar en logs..."
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
            Buscar
          </button>
        </div>
      </div>

      {/* Logs en tiempo real */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📝 Logs en Tiempo Real</h3>
        <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
          <div className="space-y-1">
            <div className="text-red-400">[2024-01-15 14:30:25] ERROR - API Server: Database connection timeout</div>
            <div className="text-yellow-400">[2024-01-15 14:30:24] WARN - LLM Server: Model loading slow, 45s elapsed</div>
            <div className="text-green-400">[2024-01-15 14:30:23] INFO - Auth System: User login successful - user123</div>
            <div className="text-blue-400">[2024-01-15 14:30:22] INFO - Training System: LoRA training started for branch Mathematics</div>
            <div className="text-green-400">[2024-01-15 14:30:21] INFO - API Server: Request processed successfully - 200 OK</div>
            <div className="text-blue-400">[2024-01-15 14:30:20] INFO - Blockchain: Transaction confirmed - TX: abc123</div>
            <div className="text-green-400">[2024-01-15 14:30:19] INFO - Memory System: Embeddings indexed - 1,247 vectors</div>
            <div className="text-yellow-400">[2024-01-15 14:30:18] WARN - Rate Limiter: Request throttled - IP: 192.168.1.100</div>
            <div className="text-blue-400">[2024-01-15 14:30:17] INFO - Dashboard: User accessed training section</div>
            <div className="text-green-400">[2024-01-15 14:30:16] INFO - Backup System: Automatic backup completed - 2.3GB</div>
          </div>
        </div>
      </div>

      {/* Estadísticas de logs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-red-400">1,247</p>
          <p className="text-sm text-gray-400">Errores Hoy</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">3,456</p>
          <p className="text-sm text-gray-400">Advertencias</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">12,347</p>
          <p className="text-sm text-gray-400">Info Logs</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">89.7%</p>
          <p className="text-sm text-gray-400">Cobertura</p>
        </div>
      </div>
    </div>
  );
}

// Componente de Debugging Tools
function DebuggingSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Herramientas de Debugging</h2>
          <p className="text-gray-400">Profiling, tracing y herramientas avanzadas de depuración</p>
        </div>
      </div>

      {/* Profiling de rendimiento */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">⚡ Profiling de Rendimiento</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium mb-3">CPU Profiling</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Función más lenta</span>
                <span className="text-red-400">embeddings_search()</span>
              </div>
              <div className="flex justify-between">
                <span>Tiempo CPU</span>
                <span className="text-red-400">2.3s</span>
              </div>
              <div className="flex justify-between">
                <span>% del total</span>
                <span className="text-red-400">45.7%</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Memory Profiling</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Peak memory</span>
                <span className="text-blue-400">8.7GB</span>
              </div>
              <div className="flex justify-between">
                <span>Memory leaks</span>
                <span className="text-blue-400">0</span>
              </div>
              <div className="flex justify-between">
                <span>GC collections</span>
                <span className="text-blue-400">47</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">I/O Profiling</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Disk reads</span>
                <span className="text-green-400">1.2GB</span>
              </div>
              <div className="flex justify-between">
                <span>Network I/O</span>
                <span className="text-green-400">847MB</span>
              </div>
              <div className="flex justify-between">
                <span>Cache hits</span>
                <span className="text-green-400">94.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tracing distribuido */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔍 Tracing Distribuido</h3>
        <div className="space-y-4">
          <div className="flex items-center space-x-4 p-3 bg-gray-700 rounded-lg">
            <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded">API</span>
            <span className="text-sm">/api/chat/send</span>
            <span className="text-sm text-gray-400">→</span>
            <span className="px-2 py-1 bg-green-600 text-white text-xs rounded">LLM</span>
            <span className="text-sm">inference()</span>
            <span className="text-sm text-green-400 ml-auto">23ms</span>
          </div>
          <div className="flex items-center space-x-4 p-3 bg-gray-700 rounded-lg">
            <span className="px-2 py-1 bg-green-600 text-white text-xs rounded">LLM</span>
            <span className="text-sm">inference()</span>
            <span className="text-sm text-gray-400">→</span>
            <span className="px-2 py-1 bg-purple-600 text-white text-xs rounded">DB</span>
            <span className="text-sm">save_conversation()</span>
            <span className="text-sm text-yellow-400 ml-auto">45ms</span>
          </div>
          <div className="flex items-center space-x-4 p-3 bg-gray-700 rounded-lg">
            <span className="px-2 py-1 bg-purple-600 text-white text-xs rounded">DB</span>
            <span className="text-sm">save_conversation()</span>
            <span className="text-sm text-gray-400">→</span>
            <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded">API</span>
            <span className="text-sm">response</span>
            <span className="text-sm text-green-400 ml-auto">12ms</span>
          </div>
        </div>
      </div>

      {/* Herramientas de debugging */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔧 Herramientas Disponibles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button className="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors text-left">
            <h4 className="font-medium mb-2">Memory Leak Detector</h4>
            <p className="text-sm text-gray-400">Detecta fugas de memoria en tiempo real</p>
          </button>
          <button className="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors text-left">
            <h4 className="font-medium mb-2">SQL Query Profiler</h4>
            <p className="text-sm text-gray-400">Analiza performance de consultas</p>
          </button>
          <button className="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors text-left">
            <h4 className="font-medium mb-2">API Response Analyzer</h4>
            <p className="text-sm text-gray-400">Inspecciona respuestas de la API</p>
          </button>
          <button className="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors text-left">
            <h4 className="font-medium mb-2">Model Inference Debugger</h4>
            <p className="text-sm text-gray-400">Debug de inferencia de modelos IA</p>
          </button>
        </div>
      </div>
    </div>
  );
}

// Componente de Documentación
function DocumentationSection() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Documentación del Sistema</h2>
          <p className="text-gray-400">Documentación completa auto-generada y guías de uso</p>
        </div>
      </div>

      {/* API Documentation */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">📚 API Documentation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Endpoints Disponibles</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Auth endpoints</span>
                <span className="text-blue-400">12</span>
              </div>
              <div className="flex justify-between">
                <span>Training endpoints</span>
                <span className="text-blue-400">8</span>
              </div>
              <div className="flex justify-between">
                <span>Blockchain endpoints</span>
                <span className="text-blue-400">15</span>
              </div>
              <div className="flex justify-between">
                <span>System endpoints</span>
                <span className="text-blue-400">6</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Documentación</h4>
            <div className="space-y-2">
              <button className="w-full text-left p-2 bg-gray-700 rounded hover:bg-gray-600 transition-colors text-sm">
                📖 OpenAPI/Swagger UI
              </button>
              <button className="w-full text-left p-2 bg-gray-700 rounded hover:bg-gray-600 transition-colors text-sm">
                📋 Postman Collection
              </button>
              <button className="w-full text-left p-2 bg-gray-700 rounded hover:bg-gray-600 transition-colors text-sm">
                📚 Guía de Integración
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Guías de usuario */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">👥 Guías de Usuario</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-700 rounded-lg">
            <h4 className="font-medium mb-2">🚀 Primeros Pasos</h4>
            <p className="text-sm text-gray-400 mb-3">Configuración inicial y registro</p>
            <button className="text-blue-400 text-sm hover:text-blue-300">Leer guía →</button>
          </div>
          <div className="p-4 bg-gray-700 rounded-lg">
            <h4 className="font-medium mb-2">🎓 Sistema de Entrenamiento</h4>
            <p className="text-sm text-gray-400 mb-3">Cómo completar ejercicios y ganar tokens</p>
            <button className="text-blue-400 text-sm hover:text-blue-300">Leer guía →</button>
          </div>
          <div className="p-4 bg-gray-700 rounded-lg">
            <h4 className="font-medium mb-2">💬 Chat con Sheily</h4>
            <p className="text-sm text-gray-400 mb-3">Interacción con IA especializada</p>
            <button className="text-blue-400 text-sm hover:text-blue-300">Leer guía →</button>
          </div>
        </div>
      </div>

      {/* Documentación técnica */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">⚙️ Documentación Técnica</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <button className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              🏗️ Arquitectura del Sistema
            </button>
            <button className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              🗄️ Esquema de Base de Datos
            </button>
            <button className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              🔧 Guía de Despliegue
            </button>
          </div>
          <div className="space-y-2">
            <button className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              🔒 Guía de Seguridad
            </button>
            <button className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              📊 Métricas y Monitoreo
            </button>
            <button className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              🚀 Optimización de Performance
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente de Configuración
function SettingsSection({ user, settings, setSettings }: {
  user: User | null;
  settings: any;
  setSettings: (settings: any) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Configuración del Sistema</h2>
          <p className="text-gray-400">Personaliza tu experiencia en Sheily AI</p>
        </div>
      </div>

      {/* Perfil de usuario */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Perfil de Usuario</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Nombre de usuario</label>
            <input
              type="text"
              defaultValue={user?.username}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <input
              type="email"
              defaultValue={user?.email}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-2">Nombre completo</label>
            <input
              type="text"
              defaultValue={user?.full_name}
              placeholder="Ingresa tu nombre completo"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex justify-end mt-4">
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors">
            💾 Guardar Cambios
          </button>
        </div>
      </div>

      {/* Configuración de apariencia */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Apariencia</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Tema oscuro</span>
              <p className="text-xs text-gray-400">Cambia entre tema claro y oscuro</p>
            </div>
            <button
              onClick={() => setSettings({...settings, theme: settings.theme === 'dark' ? 'light' : 'dark'})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.theme === 'dark' ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.theme === 'dark' ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Notificaciones</span>
              <p className="text-xs text-gray-400">Recibe notificaciones del sistema</p>
            </div>
            <button
              onClick={() => setSettings({...settings, notifications: !settings.notifications})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.notifications ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.notifications ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Autoguardado</span>
              <p className="text-xs text-gray-400">Guarda automáticamente tu progreso</p>
            </div>
            <button
              onClick={() => setSettings({...settings, autoSave: !settings.autoSave})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.autoSave ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.autoSave ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Sonido</span>
              <p className="text-xs text-gray-400">Activa sonidos de notificación</p>
            </div>
            <button
              onClick={() => setSettings({...settings, soundEnabled: !settings.soundEnabled})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.soundEnabled ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.soundEnabled ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Autenticación 2FA</span>
              <p className="text-xs text-gray-400">Seguridad adicional con 2 factores</p>
            </div>
            <button
              onClick={() => setSettings({...settings, twoFactorEnabled: !settings.twoFactorEnabled})}
              className={`w-12 h-6 rounded-full transition-colors ${settings.twoFactorEnabled ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.twoFactorEnabled ? 'translate-x-6' : 'translate-x-1'}`}></div>
            </button>
          </div>
        </div>
      </div>

      {/* Configuración de privacidad */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Privacidad y Seguridad</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Datos de uso anónimos</span>
              <p className="text-xs text-gray-400">Ayuda a mejorar Sheily AI</p>
            </div>
            <input type="checkbox" defaultChecked className="w-4 h-4" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">Sesiones activas</span>
              <p className="text-xs text-gray-400">Administra tus sesiones</p>
            </div>
            <button className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition-colors">
              Cerrar Todas
            </button>
          </div>
        </div>
      </div>

      {/* Cambio de contraseña */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Cambiar Contraseña</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Contraseña actual</label>
            <input
              type="password"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Nueva contraseña</label>
            <input
              type="password"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Confirmar nueva contraseña</label>
            <input
              type="password"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex justify-end mt-4">
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium transition-colors">
            🔑 Cambiar Contraseña
          </button>
        </div>
      </div>
    </div>
  );
}
