import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

from evaluation.quality_metrics_advanced import AdvancedQualityMetricsEvaluator
from modules.core.integration_manager import IntegrationManager
from datetime import datetime


class AdaptiveLearningAgent:
    def __init__(
        self,
        integration_manager: IntegrationManager,
        quality_evaluator: AdvancedQualityMetricsEvaluator,
        config_path: str = "utils/reinforcement_learning_config.yaml",
    ):
        """
        Agente de aprendizaje por refuerzo adaptativo

        Args:
            integration_manager (IntegrationManager): Gestor de integración
            quality_evaluator (AdvancedQualityMetricsEvaluator): Evaluador de calidad
            config_path (str): Ruta de configuración
        """
        self.logger = logging.getLogger(__name__)

        # Componentes principales
        self.integration_manager = integration_manager
        self.quality_evaluator = quality_evaluator

        # Configuración de aprendizaje por refuerzo
        self.rl_config = {
            "learning_rate": 1e-3,
            "discount_factor": 0.99,
            "exploration_rate": 0.1,
            "reward_decay": 0.95,
        }

        # Modelo de política
        self.policy_network = PolicyNetwork(
            input_size=self._get_state_size(),
            hidden_size=64,
            output_size=self._get_action_size(),
        )

        # Optimizador
        self.optimizer = optim.Adam(
            self.policy_network.parameters(), lr=self.rl_config["learning_rate"]
        )

        # Almacén de experiencias
        self.experience_buffer: List[Dict[str, Any]] = []

    def _get_state_size(self) -> int:
        """
        Obtener tamaño del estado

        Returns:
            Dimensión del vector de estado
        """
        # Ejemplo de características de estado
        return len(self._extract_state_features())

    def _get_action_size(self) -> int:
        """
        Obtener número de acciones posibles

        Returns:
            Número de acciones
        """
        # Ejemplo de acciones: ajustar parámetros de diferentes módulos
        return 10  # Placeholder

    def _extract_state_features(self, query: Optional[str] = None) -> np.ndarray:
        """
        Extraer características del estado actual

        Args:
            query (str, opcional): Consulta para contexto

        Returns:
            Vector de características de estado
        """
        # Si no hay consulta, usar últimas interacciones
        if not query:
            recent_interactions = (
                self.integration_manager.continuous_improvement.get_recent_interactions()
            )
            query = recent_interactions[-1] if recent_interactions else ""

        # Obtener métricas de calidad
        quality_metrics = self.quality_evaluator.evaluate_response_quality(query, "")

        # Obtener insights semánticos
        insights = self.integration_manager.generate_advanced_insights([query])

        # Combinar características
        state_features = [
            quality_metrics.get("coherence", 0),
            quality_metrics.get("factuality", 0),
            quality_metrics.get("relevance", 0),
            quality_metrics.get("novelty", 0),
            *insights["complexity_analysis"].get(0, [0, 0, 0]),
        ]

        return np.array(state_features)

    def select_action(self, state: np.ndarray) -> int:
        """
        Seleccionar acción usando política epsilon-greedy

        Args:
            state (np.ndarray): Estado actual

        Returns:
            Acción seleccionada
        """
        # Exploración vs explotación
        if np.random.random() < self.rl_config["exploration_rate"]:
            return np.random.randint(self._get_action_size())

        # Convertir estado a tensor
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        # Obtener distribución de probabilidad de acciones
        action_probs = self.policy_network(state_tensor)

        # Muestrear acción
        action_dist = Categorical(action_probs)
        action = action_dist.sample()

        return action.item()

    def update_policy(
        self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray
    ):
        """
        Actualizar política de aprendizaje

        Args:
            state (np.ndarray): Estado inicial
            action (int): Acción tomada
            reward (float): Recompensa recibida
            next_state (np.ndarray): Estado siguiente
        """
        # Convertir a tensores
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)
        action_tensor = torch.tensor(action).unsqueeze(0)
        reward_tensor = torch.tensor(reward)

        # Calcular valor de estado actual y siguiente
        state_value = self.policy_network(state_tensor)
        next_state_value = self.policy_network(next_state_tensor)

        # Calcular ventaja (advantage)
        advantage = reward_tensor + (
            self.rl_config["discount_factor"] * next_state_value.max()
            - state_value[0][action]
        )

        # Calcular pérdida de política
        action_log_prob = torch.log(state_value[0][action])
        policy_loss = -action_log_prob * advantage

        # Actualizar red neuronal
        self.optimizer.zero_grad()
        policy_loss.backward()
        self.optimizer.step()

    def generate_reward(self, query: str, response: str) -> float:
        """
        Generar recompensa basada en métricas de calidad

        Args:
            query (str): Consulta original
            response (str): Respuesta generada

        Returns:
            Recompensa calculada
        """
        # Evaluar calidad de la respuesta
        quality_metrics = self.quality_evaluator.evaluate_response_quality(
            query, response
        )

        # Calcular recompensa compuesta
        reward = (
            quality_metrics.get("coherence", 0) * 0.3
            + quality_metrics.get("factuality", 0) * 0.3
            + quality_metrics.get("relevance", 0) * 0.2
            + quality_metrics.get("novelty", 0) * 0.2
        )

        return reward

    def learn_from_interaction(self, query: str, response: str):
        """
        Aprender de una interacción

        Args:
            query (str): Consulta original
            response (str): Respuesta generada
        """
        # Extraer estado inicial
        initial_state = self._extract_state_features(query)

        # Seleccionar acción
        action = self.select_action(initial_state)

        # Generar recompensa
        reward = self.generate_reward(query, response)

        # Extraer estado siguiente
        next_state = self._extract_state_features(response)

        # Actualizar política
        self.update_policy(initial_state, action, reward, next_state)

        # Almacenar experiencia
        self._store_experience(query, response, action, reward)

    def _store_experience(self, query: str, response: str, action: int, reward: float):
        """
        Almacenar experiencia en buffer

        Args:
            query (str): Consulta original
            response (str): Respuesta generada
            action (int): Acción tomada
            reward (float): Recompensa recibida
        """
        experience = {
            "query": query,
            "response": response,
            "action": action,
            "reward": reward,
            "timestamp": datetime.now(),
        }

        self.experience_buffer.append(experience)

        # Limitar tamaño del buffer
        if len(self.experience_buffer) > 1000:
            self.experience_buffer.pop(0)

    def optimize_hyperparameters(self):
        """
        Optimizar hiperparámetros del agente
        """
        # Analizar buffer de experiencias
        rewards = [exp["reward"] for exp in self.experience_buffer]

        # Ajustar hiperparámetros
        if np.mean(rewards) > 0.7:
            # Reducir exploración si el rendimiento es alto
            self.rl_config["exploration_rate"] *= self.rl_config["reward_decay"]
        elif np.mean(rewards) < 0.3:
            # Aumentar exploración si el rendimiento es bajo
            self.rl_config["exploration_rate"] = min(
                self.rl_config["exploration_rate"] / self.rl_config["reward_decay"], 1.0
            )


class PolicyNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        """
        Red neuronal para política de aprendizaje por refuerzo

        Args:
            input_size (int): Tamaño de entrada
            hidden_size (int): Tamaño de capa oculta
            output_size (int): Tamaño de salida
        """
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Softmax(dim=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Propagación hacia adelante

        Args:
            x (torch.Tensor): Tensor de entrada

        Returns:
            Distribución de probabilidad de acciones
        """
        return self.network(x)
