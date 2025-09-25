#!/usr/bin/env python3
import os
import json
import hashlib
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
import math  # Added for math.log

# Importar el nuevo módulo de precisión contextual
from .contextual_accuracy import evaluate_contextual_accuracy


class SheilyRewardSystem:
    """
    Sistema de Recompensas Sheilys para aprendizaje incremental
    Gestiona la evaluación y almacenamiento de recompensas
    """

    def __init__(
        self,
        vault_path: str = "rewards/vault",
        max_vault_size: int = 10000,
        retention_days: int = 90,
    ):
        """
        Inicializar sistema de recompensas

        Args:
            vault_path (str): Directorio para almacenar recompensas
            max_vault_size (int): Número máximo de recompensas a mantener
            retention_days (int): Días para retener recompensas
        """
        self.vault_path = vault_path
        self.max_vault_size = max_vault_size
        self.retention_days = retention_days

        # Crear directorio si no existe
        os.makedirs(vault_path, exist_ok=True)

    def _calculate_sheilys(self, session_data: Dict[str, Any]) -> float:
        """
        Calcular puntuación de Sheilys con un modelo multifactorial avanzado

        Factores de evaluación:
        1. Calidad de la respuesta
        2. Complejidad del dominio
        3. Tokens procesados
        4. Novedad de la consulta
        5. Profundidad de la interacción
        6. Precisión contextual AVANZADA

        Args:
            session_data (dict): Datos completos de la sesión

        Returns:
            float: Puntuación de Sheilys (0-10)
        """
        # Configuración de pesos para cada factor
        factors = {
            "quality_score": 0.25,  # Calidad general de la respuesta
            "domain_complexity": 0.2,  # Complejidad del dominio
            "tokens_complexity": 0.15,  # Complejidad de tokens
            "novelty_factor": 0.1,  # Novedad de la consulta
            "interaction_depth": 0.15,  # Profundidad de la interacción
            "contextual_accuracy": 0.15,  # Precisión contextual AVANZADA
        }

        # Mapeo de dominios con complejidad incremental
        domain_complexity = {
            "medicina": 1.3,
            "ciberseguridad": 1.25,
            "programación": 1.2,
            "matemáticas": 1.15,
            "ciencia": 1.1,
            "ingeniería": 1.05,
            "general": 1.0,
            "entretenimiento": 0.9,
        }

        # Extraer datos de la sesión
        quality_score = session_data.get("quality_score", 0.5)
        domain = session_data.get("domain", "general")
        tokens_used = session_data.get("tokens_used", 0)
        query = session_data.get("query", "")
        response = session_data.get("response", "")

        # 1. Complejidad de dominio
        complexity = domain_complexity.get(domain, 1.0)

        # 2. Complejidad de tokens (progresiva)
        tokens_complexity = min(1.0, math.log(tokens_used + 1, 100))

        # 3. Factor de novedad (basado en longitud y unicidad de la consulta)
        def calculate_novelty(text):
            # Considerar longitud y diversidad de palabras
            words = text.split()
            unique_words = len(set(words))
            word_diversity = unique_words / len(words) if words else 0
            length_factor = min(1.0, math.log(len(text) + 1, 100))
            return word_diversity * length_factor

        novelty_factor = calculate_novelty(query)

        # 4. Profundidad de interacción
        def interaction_depth(query, response):
            # Evaluar si la respuesta aborda múltiples aspectos de la consulta
            if not query:
                return 0.0  # Sin consulta, puntuación mínima
            query_tokens = set(query.lower().split())
            response_tokens = set(response.lower().split())
            coverage = len(query_tokens.intersection(response_tokens)) / len(
                query_tokens
            )
            return min(1.0, coverage * 1.5)  # Normalizar

        interaction_score = interaction_depth(query, response)

        # 5. Precisión Contextual AVANZADA
        contextual_accuracy = evaluate_contextual_accuracy(query, response)

        # Cálculo final de Sheilys
        sheilys = (
            factors["quality_score"] * quality_score
            + factors["domain_complexity"] * complexity
            + factors["tokens_complexity"] * tokens_complexity
            + factors["novelty_factor"] * novelty_factor
            + factors["interaction_depth"] * interaction_score
            + factors["contextual_accuracy"] * contextual_accuracy
        ) * 10  # Escalar a 0-10

        # Aplicar límites y redondear
        return round(max(0, min(sheilys, 10)), 2)

    def record_reward(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registrar recompensa Sheilys para una sesión

        Args:
            session_data (dict): Datos de la sesión

        Returns:
            dict: Detalles de la recompensa registrada
        """
        # Calcular Sheilys
        sheilys = self._calculate_sheilys(session_data)

        # Preparar datos de recompensa
        reward_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": session_data.get("session_id", "unknown"),
            "domain": session_data.get("domain", "general"),
            "sheilys": sheilys,
            "details": session_data,
        }

        # Generar ID único
        reward_id = hashlib.sha256(
            json.dumps(reward_data, sort_keys=True).encode("utf-8")
        ).hexdigest()
        reward_data["reward_id"] = reward_id

        # Guardar en vault
        reward_file = os.path.join(self.vault_path, f"{reward_id}.json")
        with open(reward_file, "w", encoding="utf-8") as f:
            json.dump(reward_data, f, ensure_ascii=False, indent=2)

        return reward_data

    def get_total_sheilys(self, domain: str = None) -> float:
        """
        Obtener total de Sheilys acumulados

        Args:
            domain (str, optional): Filtrar por dominio específico

        Returns:
            float: Total de Sheilys
        """
        total_sheilys = 0.0
        cutoff_date = datetime.now(UTC) - timedelta(days=self.retention_days)

        for filename in os.listdir(self.vault_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.vault_path, filename)

                # Leer recompensa
                with open(filepath, "r", encoding="utf-8") as f:
                    reward = json.load(f)

                # Filtrar por fecha y dominio
                reward_date = datetime.fromisoformat(reward["timestamp"])
                if reward_date >= cutoff_date and (
                    domain is None or reward["domain"] == domain
                ):
                    total_sheilys += reward["sheilys"]

        return round(total_sheilys, 2)

    def cleanup_old_rewards(self):
        """
        Limpiar recompensas antiguas
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=self.retention_days)
        rewards = []

        # Recopilar recompensas
        for filename in os.listdir(self.vault_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.vault_path, filename)

                # Leer recompensa
                with open(filepath, "r", encoding="utf-8") as f:
                    reward = json.load(f)

                reward_date = datetime.fromisoformat(reward["timestamp"])

                if reward_date >= cutoff_date:
                    rewards.append((reward_date, filepath))

        # Ordenar por fecha
        rewards.sort(key=lambda x: x[0])

        # Mantener solo los más recientes
        for _, filepath in rewards[self.max_vault_size :]:
            os.remove(filepath)
