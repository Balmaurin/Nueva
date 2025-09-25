#!/usr/bin/env python3
"""
Branch Database System
======================

Sistema de base de datos para gestionar información de ramas de conocimiento.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BranchRecord:
    """Registro de rama en la base de datos"""

    id: str
    name: str
    domain: str
    description: str
    parameters: Dict[str, Any]
    created_at: str
    updated_at: str
    is_active: bool = True


class BranchDatabase:
    """Gestor de base de datos para ramas de conocimiento"""

    def __init__(self, db_path: str = "branches/branches.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        self.initialized = False

        try:
            self._initialize_database()
            self._create_default_branches()
            self.initialized = True
            self.logger.info("✅ BranchDatabase inicializado")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando BranchDatabase: {e}")
            self.initialized = False

    def _initialize_database(self):
        """Inicializar esquema de base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS branches (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    description TEXT,
                    parameters TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS branch_metrics (
                    branch_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    recorded_at TEXT,
                    FOREIGN KEY(branch_id) REFERENCES branches(id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS branch_usage (
                    branch_id TEXT,
                    query TEXT,
                    response_quality REAL,
                    used_at TEXT,
                    FOREIGN KEY(branch_id) REFERENCES branches(id)
                )
            """
            )

            conn.commit()

    def _create_default_branches(self):
        """Crear ramas por defecto si no existen"""
        default_branches = [
            {
                "id": "programming",
                "name": "Programming & Development",
                "domain": "programming",
                "description": "Specialized in programming languages, software development, and coding best practices",
                "parameters": {
                    "temperature": 0.3,
                    "max_tokens": 1024,
                    "focus_areas": [
                        "python",
                        "javascript",
                        "algorithms",
                        "data_structures",
                    ],
                    "expertise_level": "advanced",
                },
            },
            {
                "id": "ai_ml",
                "name": "Artificial Intelligence & Machine Learning",
                "domain": "ai",
                "description": "Expert in AI concepts, machine learning algorithms, and neural networks",
                "parameters": {
                    "temperature": 0.5,
                    "max_tokens": 1536,
                    "focus_areas": [
                        "machine_learning",
                        "neural_networks",
                        "nlp",
                        "computer_vision",
                    ],
                    "expertise_level": "expert",
                },
            },
            {
                "id": "database",
                "name": "Database Management",
                "domain": "database",
                "description": "Specialized in database design, SQL, and data management",
                "parameters": {
                    "temperature": 0.2,
                    "max_tokens": 512,
                    "focus_areas": [
                        "sql",
                        "database_design",
                        "optimization",
                        "data_modeling",
                    ],
                    "expertise_level": "advanced",
                },
            },
            {
                "id": "general",
                "name": "General Knowledge",
                "domain": "general",
                "description": "General purpose knowledge and conversation",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "focus_areas": [
                        "general_knowledge",
                        "conversation",
                        "problem_solving",
                    ],
                    "expertise_level": "intermediate",
                },
            },
        ]

        for branch_data in default_branches:
            if not self.get_branch(branch_data["id"]):
                self.create_branch(
                    branch_data["id"],
                    branch_data["name"],
                    branch_data["domain"],
                    branch_data["description"],
                    branch_data["parameters"],
                )

    def create_branch(
        self,
        branch_id: str,
        name: str,
        domain: str,
        description: str,
        parameters: Dict[str, Any],
    ) -> bool:
        """Crear nueva rama en la base de datos"""
        try:
            now = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO branches 
                    (id, name, domain, description, parameters, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        branch_id,
                        name,
                        domain,
                        description,
                        json.dumps(parameters),
                        now,
                        now,
                        True,
                    ),
                )
                conn.commit()

            self.logger.info(f"✅ Rama creada: {branch_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error creando rama {branch_id}: {e}")
            return False

    def get_branch(self, branch_id: str) -> Optional[BranchRecord]:
        """Obtener rama por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                result = cursor.execute(
                    "SELECT * FROM branches WHERE id = ?", (branch_id,)
                ).fetchone()

                if result:
                    return BranchRecord(
                        id=result["id"],
                        name=result["name"],
                        domain=result["domain"],
                        description=result["description"],
                        parameters=json.loads(result["parameters"]),
                        created_at=result["created_at"],
                        updated_at=result["updated_at"],
                        is_active=bool(result["is_active"]),
                    )
                return None

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo rama {branch_id}: {e}")
            return None

    def list_branches(self, active_only: bool = True) -> List[BranchRecord]:
        """Listar todas las ramas"""
        branches = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = "SELECT * FROM branches"
                params = []

                if active_only:
                    query += " WHERE is_active = ?"
                    params.append(True)

                query += " ORDER BY name"

                results = cursor.execute(query, params).fetchall()

                for row in results:
                    branches.append(
                        BranchRecord(
                            id=row["id"],
                            name=row["name"],
                            domain=row["domain"],
                            description=row["description"],
                            parameters=json.loads(row["parameters"]),
                            created_at=row["created_at"],
                            updated_at=row["updated_at"],
                            is_active=bool(row["is_active"]),
                        )
                    )

        except Exception as e:
            self.logger.error(f"❌ Error listando ramas: {e}")

        return branches

    def update_branch(self, branch_id: str, **kwargs) -> bool:
        """Actualizar rama existente"""
        try:
            branch = self.get_branch(branch_id)
            if not branch:
                return False

            # Construir query de actualización dinámicamente
            updates = []
            params = []

            for key, value in kwargs.items():
                if key in ["name", "domain", "description", "is_active"]:
                    updates.append(f"{key} = ?")
                    params.append(value)
                elif key == "parameters":
                    updates.append("parameters = ?")
                    params.append(json.dumps(value))

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(branch_id)

                query = f"UPDATE branches SET {', '.join(updates)} WHERE id = ?"

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(query, params)
                    conn.commit()

                self.logger.info(f"✅ Rama actualizada: {branch_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Error actualizando rama {branch_id}: {e}")
            return False

    def record_usage(self, branch_id: str, query: str, response_quality: float):
        """Registrar uso de una rama"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO branch_usage (branch_id, query, response_quality, used_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (branch_id, query, response_quality, datetime.now().isoformat()),
                )
                conn.commit()

        except Exception as e:
            self.logger.error(f"❌ Error registrando uso de rama {branch_id}: {e}")

    def get_usage_stats(self, branch_id: str, days: int = 7) -> Dict[str, Any]:
        """Obtener estadísticas de uso de una rama"""
        try:
            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total de usos
                total_uses = cursor.execute(
                    """
                    SELECT COUNT(*) FROM branch_usage 
                    WHERE branch_id = ? AND used_at >= ?
                """,
                    (branch_id, cutoff_date.isoformat()),
                ).fetchone()[0]

                # Calidad promedio
                avg_quality = cursor.execute(
                    """
                    SELECT AVG(response_quality) FROM branch_usage 
                    WHERE branch_id = ? AND used_at >= ?
                """,
                    (branch_id, cutoff_date.isoformat()),
                ).fetchone()[0]

                return {
                    "branch_id": branch_id,
                    "period_days": days,
                    "total_uses": total_uses,
                    "average_quality": round(avg_quality or 0.0, 2),
                    "last_updated": datetime.now().isoformat(),
                }

        except Exception as e:
            self.logger.error(
                f"❌ Error obteniendo estadísticas de rama {branch_id}: {e}"
            )
            return {"branch_id": branch_id, "error": str(e)}

    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema de base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                total_branches = cursor.execute(
                    "SELECT COUNT(*) FROM branches"
                ).fetchone()[0]
                active_branches = cursor.execute(
                    "SELECT COUNT(*) FROM branches WHERE is_active = 1"
                ).fetchone()[0]
                total_usage_records = cursor.execute(
                    "SELECT COUNT(*) FROM branch_usage"
                ).fetchone()[0]

                return {
                    "initialized": self.initialized,
                    "database_path": str(self.db_path),
                    "total_branches": total_branches,
                    "active_branches": active_branches,
                    "total_usage_records": total_usage_records,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {"initialized": False, "error": str(e)}
