#!/usr/bin/env python3
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List


class SessionTracker:
    """
    Sistema de tracking de sesiones para el sistema de recompensas Sheilys
    Rastrea la utilidad de las conversaciones para aprendizaje incremental
    """

    def __init__(
        self,
        storage_path: str = "rewards/sessions",
        max_sessions: int = 1000,
        retention_days: int = 90,
    ):
        """
        Inicializar el tracker de sesiones

        Args:
            storage_path (str): Directorio para almacenar sesiones
            max_sessions (int): Número máximo de sesiones a mantener
            retention_days (int): Días para retener sesiones
        """
        self.storage_path = storage_path
        self.max_sessions = max_sessions
        self.retention_days = retention_days

        # Crear directorio si no existe
        os.makedirs(storage_path, exist_ok=True)

    def _generate_session_id(self, session_data: Dict[str, Any]) -> str:
        """
        Generar un ID único para la sesión basado en sus contenidos

        Args:
            session_data (dict): Datos de la sesión

        Returns:
            str: Hash SHA256 de la sesión
        """
        # Convertir datos a cadena para hashear
        session_str = json.dumps(session_data, sort_keys=True)
        return hashlib.sha256(session_str.encode("utf-8")).hexdigest()

    def track_session(
        self, domain: str, query: str, response: str, quality_score: float
    ) -> Dict[str, Any]:
        """
        Registrar una sesión para evaluación de recompensas

        Args:
            domain (str): Dominio de la conversación
            query (str): Consulta del usuario
            response (str): Respuesta del modelo
            quality_score (float): Puntuación de calidad de la sesión

        Returns:
            dict: Detalles de la sesión registrada
        """
        # Preparar datos de sesión
        session_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": domain,
            "query": query,
            "response": response,
            "quality_score": quality_score,
            "tokens_used": len(query.split()) + len(response.split()),
        }

        # Generar ID de sesión
        session_id = self._generate_session_id(session_data)
        session_data["session_id"] = session_id

        # Guardar sesión
        session_file = os.path.join(self.storage_path, f"{session_id}.json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        return session_data

    def get_useful_sessions(
        self, min_quality_score: float = 0.7, domain: str = None
    ) -> List[Dict[str, Any]]:
        """
        Obtener sesiones útiles para entrenamiento

        Args:
            min_quality_score (float): Puntuación mínima para considerar útil
            domain (str, optional): Filtrar por dominio específico

        Returns:
            list: Sesiones útiles
        """
        useful_sessions = []
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_path, filename)

                # Leer sesión
                with open(filepath, "r", encoding="utf-8") as f:
                    session = json.load(f)

                # Filtrar por fecha, puntuación y dominio
                session_date = datetime.fromisoformat(session["timestamp"])
                if (
                    session_date >= cutoff_date
                    and session["quality_score"] >= min_quality_score
                    and (domain is None or session["domain"] == domain)
                ):
                    useful_sessions.append(session)

        # Ordenar por puntuación de calidad (descendente)
        useful_sessions.sort(key=lambda x: x["quality_score"], reverse=True)

        # Limitar número de sesiones
        return useful_sessions[: self.max_sessions]

    def cleanup_old_sessions(self):
        """
        Limpiar sesiones antiguas
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_path, filename)

                # Leer fecha de sesión
                with open(filepath, "r", encoding="utf-8") as f:
                    session = json.load(f)

                session_date = datetime.fromisoformat(session["timestamp"])

                # Eliminar si es más antiguo que la fecha de corte
                if session_date < cutoff_date:
                    os.remove(filepath)
