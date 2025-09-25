'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

const tabs = ['overview', 'chat', 'branches', 'exercises'] as const;
type DashboardTab = (typeof tabs)[number];

type BranchProgress = {
  id: number;
  exercise_type: string;
  level: number;
  accuracy: number | null;
  attempts: number;
  completed: boolean;
  tokens_awarded: number;
  verification_status: string;
  last_reviewed_at: string | null;
};

type Branch = {
  id: number;
  branch_key: string;
  name: string;
  domain: string | null;
  description: string | null;
  competency_map?: unknown;
  created_at: string;
  updated_at: string;
  progress?: BranchProgress[];
};

type ExerciseOption = {
  option_key?: string;
  content: string;
  feedback?: string | null;
};

type Exercise = {
  id: number;
  branch_id: number | string;
  branch_name: string | null;
  scope: string | null;
  level: number;
  exercise_type: string;
  question: string;
  answer?: string;
  explanation?: string;
  validation_source?: string;
  confidence_score?: number | null;
  options_detail?: ExerciseOption[];
};

type ChatMessage = {
  id: number;
  text: string;
  sender: 'user' | 'assistant' | 'system';
  timestamp: Date;
};

const formatDate = (value: string | null) => {
  if (!value) {
    return '—';
  }
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
};

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isAuthenticated, isLoading, token } = useAuth();

  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');
  const [selectedBranchKey, setSelectedBranchKey] = useState<string | null>(null);

  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesLoading, setBranchesLoading] = useState(false);
  const [branchesError, setBranchesError] = useState<string | null>(null);

  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [exercisesLoading, setExercisesLoading] = useState(false);
  const [exercisesError, setExercisesError] = useState<string | null>(null);

  const [tokenBalance, setTokenBalance] = useState<number | null>(null);
  const [tokensLoading, setTokensLoading] = useState(false);
  const [tokensError, setTokensError] = useState<string | null>(null);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const chatMessagesRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (!token || !isAuthenticated) {
      setBranches([]);
      setSelectedBranchKey(null);
      return;
    }

    const controller = new AbortController();
    setBranchesLoading(true);
    setBranchesError(null);

    fetch(`${API_BASE}/api/branches?includeProgress=true`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const payload = await response.json().catch(() => ({ error: 'No se pudo obtener la lista de ramas' }));
          throw new Error(payload.error || 'No se pudo obtener la lista de ramas');
        }
        return response.json();
      })
      .then((data: { branches: Branch[] }) => {
        setBranches(data.branches ?? []);
        if (data.branches?.length) {
          setSelectedBranchKey((current) => current ?? data.branches[0].branch_key);
        }
      })
      .catch((error: Error) => {
        if (controller.signal.aborted) {
          return;
        }
        setBranchesError(error.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setBranchesLoading(false);
        }
      });

    return () => controller.abort();
  }, [isAuthenticated, token]);

  useEffect(() => {
    if (!token || !isAuthenticated) {
      setTokenBalance(null);
      return;
    }

    const controller = new AbortController();
    setTokensLoading(true);
    setTokensError(null);

    fetch(`${API_BASE}/api/auth/tokens`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const payload = await response.json().catch(() => ({ error: 'No se pudo obtener el balance de tokens' }));
          throw new Error(payload.error || 'No se pudo obtener el balance de tokens');
        }
        return response.json();
      })
      .then((data: { tokens: number }) => {
        setTokenBalance(typeof data.tokens === 'number' ? data.tokens : 0);
      })
      .catch((error: Error) => {
        if (controller.signal.aborted) {
          return;
        }
        setTokensError(error.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setTokensLoading(false);
        }
      });

    return () => controller.abort();
  }, [isAuthenticated, token]);

  useEffect(() => {
    if (!token || !isAuthenticated || !selectedBranchKey) {
      setExercises([]);
      return;
    }

    const controller = new AbortController();
    setExercisesLoading(true);
    setExercisesError(null);

    fetch(`${API_BASE}/api/branches/${encodeURIComponent(selectedBranchKey)}/exercises`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const payload = await response.json().catch(() => ({ error: 'No se pudieron obtener los ejercicios' }));
          throw new Error(payload.error || 'No se pudieron obtener los ejercicios');
        }
        return response.json();
      })
      .then((data: { exercises: Exercise[] }) => {
        setExercises(data.exercises ?? []);
      })
      .catch((error: Error) => {
        if (controller.signal.aborted) {
          return;
        }
        setExercisesError(error.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setExercisesLoading(false);
        }
      });

    return () => controller.abort();
  }, [isAuthenticated, token, selectedBranchKey]);

  useEffect(() => {
    if (!chatMessagesRef.current) {
      return;
    }
    chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
  }, [chatMessages]);

  const selectedBranch = useMemo(
    () => branches.find((branch) => branch.branch_key === selectedBranchKey) ?? null,
    [branches, selectedBranchKey]
  );

  const handleLogout = () => {
    logout();
    router.replace('/');
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !token) {
      return;
    }

    const content = chatInput.trim();
    setChatInput('');
    setChatLoading(true);

    const userMessage: ChatMessage = {
      id: Date.now(),
      text: content,
      sender: 'user',
      timestamp: new Date(),
    };
    setChatMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: content,
          branch: selectedBranchKey ?? undefined,
          session_id: chatSessionId ?? undefined,
          user_id: user?.id,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({ error: 'No se pudo obtener respuesta del asistente' }));
        throw new Error(payload.error || 'No se pudo obtener respuesta del asistente');
      }

      const data = await response.json();
      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        text: data.response ?? 'El servidor respondió sin contenido.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, assistantMessage]);

      if (typeof data.session_id === 'string' && data.session_id) {
        setChatSessionId(data.session_id);
      }
    } catch (error) {
      const systemMessage: ChatMessage = {
        id: Date.now() + 2,
        text: error instanceof Error ? error.message : 'Error inesperado en el chat',
        sender: 'system',
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, systemMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendChatMessage();
    }
  };

  const renderTabContent = () => {
    if (isLoading) {
      return <p className="text-slate-300">Cargando sesión...</p>;
    }

    if (!isAuthenticated) {
      return <p className="text-slate-300">Redirigiendo al inicio...</p>;
    }

    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
              <h2 className="text-xl font-semibold text-white">Perfil</h2>
              <dl className="mt-4 grid gap-4 text-sm text-slate-200 sm:grid-cols-2">
                <div>
                  <dt className="text-slate-400">Usuario</dt>
                  <dd className="text-white">{user?.username ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Correo</dt>
                  <dd className="text-white">{user?.email ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Rol</dt>
                  <dd className="text-white">{user?.role ?? '—'}</dd>
                </div>
              </dl>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
              <h2 className="text-xl font-semibold text-white">Tokens disponibles</h2>
              {tokensLoading ? (
                <p className="text-slate-300">Consultando balance...</p>
              ) : tokensError ? (
                <p className="text-red-400">{tokensError}</p>
              ) : (
                <p className="text-3xl font-bold text-cyan-400">{tokenBalance ?? 0}</p>
              )}
            </div>
          </div>
        );
      case 'chat':
        return (
          <div className="flex h-[70vh] flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
            <div
              ref={chatMessagesRef}
              className="flex-1 space-y-4 overflow-y-auto pr-2"
            >
              {chatMessages.length === 0 ? (
                <p className="text-slate-400">Inicia una conversación para recibir ayuda contextualizada.</p>
              ) : (
                chatMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`max-w-3xl rounded-lg border px-4 py-3 text-sm transition-colors ${
                      message.sender === 'user'
                        ? 'self-end border-blue-500/40 bg-blue-500/10 text-blue-100'
                        : message.sender === 'assistant'
                        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100'
                        : 'border-amber-500/40 bg-amber-500/10 text-amber-100'
                    }`}
                  >
                    <div className="mb-1 flex items-center justify-between text-xs uppercase tracking-wide">
                      <span>
                        {message.sender === 'user'
                          ? 'Tú'
                          : message.sender === 'assistant'
                          ? 'Sheily'
                          : 'Sistema'}
                      </span>
                      <span className="text-slate-400">{message.timestamp.toLocaleTimeString()}</span>
                    </div>
                    <p className="whitespace-pre-line leading-relaxed">{message.text}</p>
                  </div>
                ))
              )}
            </div>

            <div className="mt-4 space-y-3">
              <label className="text-sm font-medium text-slate-300">
                Rama activa
                <select
                  value={selectedBranchKey ?? ''}
                  onChange={(event) => setSelectedBranchKey(event.target.value || null)}
                  className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
                >
                  <option value="">Sin contexto específico</option>
                  {branches.map((branch) => (
                    <option key={branch.branch_key} value={branch.branch_key}>
                      {branch.name}
                    </option>
                  ))}
                </select>
              </label>

              <textarea
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                onKeyDown={handleChatKeyDown}
                placeholder="Escribe tu mensaje y pulsa Enter para enviar"
                rows={4}
                className="w-full rounded-md border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
              />
              <div className="flex justify-end gap-3">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setChatMessages([]);
                    setChatSessionId(null);
                  }}
                >
                  Limpiar historial
                </Button>
                <Button type="button" variant="glow" disabled={chatLoading || !chatInput.trim()} onClick={sendChatMessage}>
                  {chatLoading ? 'Enviando…' : 'Enviar'}
                </Button>
              </div>
            </div>
          </div>
        );
      case 'branches':
        return (
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
            <h2 className="text-xl font-semibold text-white">Ramas disponibles</h2>
            {branchesLoading ? (
              <p className="mt-4 text-slate-300">Cargando ramas…</p>
            ) : branchesError ? (
              <p className="mt-4 text-red-400">{branchesError}</p>
            ) : branches.length === 0 ? (
              <p className="mt-4 text-slate-300">No se encontraron ramas registradas.</p>
            ) : (
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                {branches.map((branch) => (
                  <article
                    key={branch.branch_key}
                    className="rounded-lg border border-slate-800 bg-slate-950/50 p-5"
                  >
                    <header className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{branch.name}</h3>
                        <p className="text-xs uppercase tracking-wide text-slate-400">{branch.branch_key}</p>
                      </div>
                      <Button
                        type="button"
                        size="sm"
                        variant={selectedBranchKey === branch.branch_key ? 'default' : 'outline'}
                        onClick={() => setSelectedBranchKey(branch.branch_key)}
                      >
                        {selectedBranchKey === branch.branch_key ? 'Seleccionada' : 'Seleccionar'}
                      </Button>
                    </header>
                    {branch.description ? (
                      <p className="mt-3 text-sm leading-relaxed text-slate-300">{branch.description}</p>
                    ) : (
                      <p className="mt-3 text-sm text-slate-500">Sin descripción registrada.</p>
                    )}
                    {branch.progress && branch.progress.length > 0 ? (
                      <div className="mt-4 space-y-2 text-sm text-slate-300">
                        <p className="text-slate-400">Progreso:</p>
                        <ul className="space-y-1 text-xs">
                          {branch.progress.map((entry) => (
                            <li key={entry.id} className="rounded border border-slate-800/60 bg-slate-950/60 p-2">
                              <div className="flex flex-wrap items-center justify-between gap-2">
                                <span className="font-medium text-cyan-300">
                                  {entry.exercise_type} · Nivel {entry.level}
                                </span>
                                <span className="text-slate-400">
                                  {entry.completed ? 'Completado' : 'En progreso'} ({entry.accuracy ?? 0}% precisión)
                                </span>
                              </div>
                              <div className="mt-1 flex flex-wrap items-center justify-between gap-2 text-slate-500">
                                <span>{entry.attempts} intento(s)</span>
                                <span>{entry.tokens_awarded} tokens</span>
                                <span>Última revisión: {formatDate(entry.last_reviewed_at)}</span>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <p className="mt-4 text-sm text-slate-500">Aún no registras progreso en esta rama.</p>
                    )}
                  </article>
                ))}
              </div>
            )}
          </div>
        );
      case 'exercises':
        return (
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white">Ejercicios</h2>
                  <p className="text-sm text-slate-400">
                    Selecciona una rama para consultar los ejercicios oficiales asociados.
                  </p>
                </div>
                <label className="text-sm text-slate-300">
                  Rama
                  <select
                    value={selectedBranchKey ?? ''}
                    onChange={(event) => setSelectedBranchKey(event.target.value || null)}
                    className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="">Selecciona una rama</option>
                    {branches.map((branch) => (
                      <option key={branch.branch_key} value={branch.branch_key}>
                        {branch.name}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>

            {selectedBranchKey ? (
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
                {exercisesLoading ? (
                  <p className="text-slate-300">Cargando ejercicios…</p>
                ) : exercisesError ? (
                  <p className="text-red-400">{exercisesError}</p>
                ) : exercises.length === 0 ? (
                  <p className="text-slate-300">No hay ejercicios registrados para esta rama.</p>
                ) : (
                  <ul className="space-y-4">
                    {exercises.map((exercise) => (
                      <li
                        key={exercise.id}
                        className="rounded-lg border border-slate-800 bg-slate-950/50 p-4"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 text-xs uppercase tracking-wide text-slate-400">
                          <span>{exercise.exercise_type}</span>
                          <span>Nivel {exercise.level}</span>
                        </div>
                        <h3 className="mt-2 text-lg font-semibold text-white">{exercise.question}</h3>
                        <p className="mt-2 text-sm leading-relaxed text-slate-300">{exercise.question}</p>
                        {exercise.options_detail && exercise.options_detail.length > 0 && (
                          <div className="mt-3 space-y-1 text-sm text-slate-200">
                            {exercise.options_detail.map((option, index) => (
                              <div key={`${exercise.id}-${option.option_key ?? index}`} className="flex gap-2">
                                <span className="font-semibold text-cyan-300">
                                  {option.option_key ?? String.fromCharCode(65 + index)}.
                                </span>
                                <span>{option.content}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-6 text-center text-slate-400">
                Selecciona una rama para consultar los ejercicios disponibles.
              </div>
            )}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <h1 className="text-2xl font-semibold">Panel de control</h1>
            {selectedBranch ? (
              <p className="text-sm text-slate-400">
                Rama activa: <span className="text-cyan-300">{selectedBranch.name}</span>
              </p>
            ) : (
              <p className="text-sm text-slate-500">Selecciona una rama para personalizar la experiencia.</p>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right text-sm text-slate-300">
              <p>{user?.username}</p>
              <p className="text-slate-500">{user?.email}</p>
            </div>
            <Button type="button" variant="outline" onClick={handleLogout}>
              Cerrar sesión
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <nav className="flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`rounded-full px-4 py-2 text-sm capitalize transition-colors ${
                activeTab === tab
                  ? 'bg-cyan-600 text-white shadow-lg'
                  : 'bg-slate-900/60 text-slate-300 hover:bg-slate-900'
              }`}
            >
              {tab === 'overview' ? 'Resumen' : tab === 'chat' ? 'Chat' : tab === 'branches' ? 'Ramas' : 'Ejercicios'}
            </button>
          ))}
        </nav>

        <section className="mt-8">{renderTabContent()}</section>
      </main>
    </div>
  );
}
