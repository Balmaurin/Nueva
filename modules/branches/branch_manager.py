#!/usr/bin/env python3
"""
Sistema de Gestión de Branches
Gestiona las ramas de conocimiento y especialización del sistema
"""

import os
import json
import sqlite3
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import threading
import hashlib
from dataclasses import dataclass, asdict


@dataclass
class Branch:
    """Estructura de datos para una rama de conocimiento"""

    id: str
    name: str
    description: str
    category: str
    keywords: List[str]
    model_name: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    metadata: Dict[str, Any] = None


class BranchManager:
    """Gestor completo de branches con funciones reales"""

    def __init__(self, branches_dir: str = "branches"):
        self.branches_dir = Path(branches_dir)
        self.branches_dir.mkdir(exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Inicializar base de datos
        self.db_path = self.branches_dir / "branches.db"
        self._init_database()

        # Lock para operaciones thread-safe
        self._lock = threading.Lock()

        # Cargar configuración base
        self.base_config_path = self.branches_dir / "base_branches.json"
        self._load_base_config()

        self.logger.info(f"✅ BranchManager inicializado en {self.branches_dir}")

    def _init_database(self):
        """Inicializar base de datos SQLite para branches"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS branches (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_branch_name ON branches(name)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_branch_category ON branches(category)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_branch_status ON branches(status)
            """
            )

    def _load_base_config(self):
        """Cargar configuración base de branches"""
        if self.base_config_path.exists():
            try:
                with open(self.base_config_path, "r", encoding="utf-8") as f:
                    self.base_config = json.load(f)
                self.logger.info(
                    f"📋 Configuración base cargada: {len(self.base_config.get('domains', []))} dominios"
                )
            except Exception as e:
                self.logger.error(f"❌ Error cargando configuración base: {e}")
                self.base_config = {"domains": []}
        else:
            self.base_config = {"domains": []}
            self._create_default_base_config()

    def _create_default_base_config(self):
        """Crear configuración base por defecto"""
        default_config = {
            "domains": [
                {
                    "name": "general",
                    "keywords": ["general", "común", "básico"],
                    "description": "Rama general para conversaciones cotidianas",
                },
                {
                    "name": "programación",
                    "keywords": ["código", "python", "bug", "error"],
                    "description": "Rama especializada en programación y desarrollo",
                },
                {
                    "name": "finanzas",
                    "keywords": ["bolsa", "precio", "btc", "eur"],
                    "description": "Rama especializada en finanzas y economía",
                },
            ]
        }

        with open(self.base_config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        self.base_config = default_config
        self.logger.info("📋 Configuración base por defecto creada")

    def create_branch(
        self,
        name: str,
        description: str,
        category: str,
        keywords: List[str],
        model_name: str = "models/custom/shaili-personal-model",
        config: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Crear nueva rama de conocimiento"""
        with self._lock:
            try:
                # Verificar que el nombre no exista
                if self.get_branch_by_name(name):
                    raise ValueError(f"Ya existe una rama con el nombre: {name}")

                # Generar ID único
                branch_id = self._generate_branch_id(name, category)

                # Crear directorio de la rama
                branch_dir = self.branches_dir / name
                branch_dir.mkdir(exist_ok=True)

                # Configuración por defecto
                default_config = {
                    "model_name": model_name,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                    "special_tokens": [],
                    "context_window": 4096,
                }

                if config:
                    default_config.update(config)

                # Crear archivo de configuración de la rama
                branch_config_file = branch_dir / "config.json"
                branch_config = {
                    "id": branch_id,
                    "name": name,
                    "description": description,
                    "category": category,
                    "keywords": keywords,
                    "model_name": model_name,
                    "config": default_config,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "metadata": metadata or {},
                }

                with open(branch_config_file, "w", encoding="utf-8") as f:
                    json.dump(branch_config, f, indent=2, ensure_ascii=False)

                # Registrar en base de datos
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO branches 
                        (id, name, description, category, keywords, model_name, config, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            branch_id,
                            name,
                            description,
                            category,
                            json.dumps(keywords),
                            model_name,
                            json.dumps(default_config),
                            json.dumps(metadata or {}),
                        ),
                    )

                self.logger.info(f"✅ Rama {name} creada exitosamente")
                return branch_id

            except Exception as e:
                self.logger.error(f"❌ Error creando rama {name}: {e}")
                raise

    def _generate_branch_id(self, name: str, category: str) -> str:
        """Generar ID único para la rama"""
        content = f"{name}:{category}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_branch(self, branch_id: str) -> Optional[Branch]:
        """Obtener rama por ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM branches WHERE id = ? AND status = 'active'
            """,
                (branch_id,),
            )
            row = cursor.fetchone()

            if row:
                return Branch(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    category=row[3],
                    keywords=json.loads(row[4]),
                    model_name=row[5],
                    config=json.loads(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    status=row[9],
                    metadata=json.loads(row[10]) if row[10] else {},
                )
            return None

    def get_branch_by_name(self, name: str) -> Optional[Branch]:
        """Obtener rama por nombre"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM branches WHERE name = ? AND status = 'active'
            """,
                (name,),
            )
            row = cursor.fetchone()

            if row:
                return Branch(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    category=row[3],
                    keywords=json.loads(row[4]),
                    model_name=row[5],
                    config=json.loads(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    status=row[9],
                    metadata=json.loads(row[10]) if row[10] else {},
                )
            return None

    def list_branches(
        self, category: str = None, status: str = "active", limit: int = 100
    ) -> List[Branch]:
        """Listar ramas con filtros"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM branches WHERE 1=1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            branches = []

            for row in cursor.fetchall():
                branches.append(
                    Branch(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        category=row[3],
                        keywords=json.loads(row[4]),
                        model_name=row[5],
                        config=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        updated_at=datetime.fromisoformat(row[8]),
                        status=row[9],
                        metadata=json.loads(row[10]) if row[10] else {},
                    )
                )

            return branches

    def update_branch(self, branch_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar rama existente"""
        with self._lock:
            try:
                # Obtener rama actual
                branch = self.get_branch(branch_id)
                if not branch:
                    self.logger.error(f"❌ Rama {branch_id} no encontrada")
                    return False

                # Actualizar campos permitidos
                allowed_fields = [
                    "description",
                    "keywords",
                    "model_name",
                    "config",
                    "metadata",
                ]
                update_data = {}

                for field, value in updates.items():
                    if field in allowed_fields:
                        update_data[field] = value

                if not update_data:
                    self.logger.warning("⚠️ No hay campos válidos para actualizar")
                    return False

                # Actualizar en base de datos
                with sqlite3.connect(self.db_path) as conn:
                    set_clause = ", ".join(
                        [f"{field} = ?" for field in update_data.keys()]
                    )
                    set_clause += ", updated_at = ?"

                    values = []
                    for field in update_data.keys():
                        if field in ["keywords", "config", "metadata"]:
                            values.append(json.dumps(update_data[field]))
                        else:
                            values.append(update_data[field])
                    values.append(datetime.now().isoformat())
                    values.append(branch_id)

                    conn.execute(
                        f"""
                        UPDATE branches 
                        SET {set_clause}
                        WHERE id = ?
                    """,
                        values,
                    )

                # Actualizar archivo de configuración
                branch_dir = self.branches_dir / branch.name
                branch_config_file = branch_dir / "config.json"

                if branch_config_file.exists():
                    with open(branch_config_file, "r", encoding="utf-8") as f:
                        branch_config = json.load(f)

                    # Actualizar configuración
                    for field, value in update_data.items():
                        if field in ["keywords", "config", "metadata"]:
                            branch_config[field] = value
                        else:
                            branch_config[field] = value

                    branch_config["updated_at"] = datetime.now().isoformat()

                    with open(branch_config_file, "w", encoding="utf-8") as f:
                        json.dump(branch_config, f, indent=2, ensure_ascii=False)

                self.logger.info(f"✅ Rama {branch_id} actualizada exitosamente")
                return True

            except Exception as e:
                self.logger.error(f"❌ Error actualizando rama {branch_id}: {e}")
                return False

    def delete_branch(self, branch_id: str, permanent: bool = False) -> bool:
        """Eliminar rama"""
        with self._lock:
            try:
                branch = self.get_branch(branch_id)
                if not branch:
                    self.logger.error(f"❌ Rama {branch_id} no encontrada")
                    return False

                if permanent:
                    # Eliminación permanente
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM branches WHERE id = ?", (branch_id,))

                    # Eliminar directorio
                    branch_dir = self.branches_dir / branch.name
                    if branch_dir.exists():
                        shutil.rmtree(branch_dir)

                    self.logger.info(f"🗑️ Rama {branch_id} eliminada permanentemente")
                else:
                    # Eliminación lógica (marcar como inactiva)
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            """
                            UPDATE branches 
                            SET status = 'deleted', updated_at = ?
                            WHERE id = ?
                        """,
                            (datetime.now().isoformat(), branch_id),
                        )

                    self.logger.info(f"🗑️ Rama {branch_id} marcada como eliminada")

                return True

            except Exception as e:
                self.logger.error(f"❌ Error eliminando rama {branch_id}: {e}")
                return False

    def search_branches(self, query: str, limit: int = 10) -> List[Branch]:
        """Buscar ramas por texto"""
        query_lower = query.lower()
        all_branches = self.list_branches(status="active", limit=1000)
        results = []

        for branch in all_branches:
            # Buscar en nombre, descripción, categoría y palabras clave
            search_text = f"{branch.name} {branch.description} {branch.category} {' '.join(branch.keywords)}".lower()

            if query_lower in search_text:
                results.append(branch)

            if len(results) >= limit:
                break

        return results

    def get_branch_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de ramas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_branches,
                    COUNT(DISTINCT category) as unique_categories,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_branches,
                    COUNT(CASE WHEN status = 'deleted' THEN 1 END) as deleted_branches,
                    MIN(created_at) as earliest_branch,
                    MAX(updated_at) as latest_update
                FROM branches
            """
            )
            result = cursor.fetchone()

            return {
                "total_branches": result[0],
                "unique_categories": result[1],
                "active_branches": result[2],
                "deleted_branches": result[3],
                "earliest_branch": result[4],
                "latest_update": result[5],
            }

    def export_branch(self, branch_id: str, export_path: str = None) -> str:
        """Exportar rama completa"""
        try:
            branch = self.get_branch(branch_id)
            if not branch:
                raise ValueError(f"Rama {branch_id} no encontrada")

            # Crear directorio de exportación
            if export_path:
                export_dir = Path(export_path)
            else:
                export_dir = Path("exports")

            export_dir.mkdir(exist_ok=True)

            # Crear archivo de exportación
            export_file = (
                export_dir
                / f"branch_{branch.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            export_data = {
                "branch": asdict(branch),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📤 Rama {branch_id} exportada a {export_file}")
            return str(export_file)

        except Exception as e:
            self.logger.error(f"❌ Error exportando rama {branch_id}: {e}")
            raise

    def import_branch(self, import_file: str) -> str:
        """Importar rama desde archivo"""
        try:
            with open(import_file, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            branch_data = import_data.get("branch", {})

            # Crear nueva rama con datos importados
            branch_id = self.create_branch(
                name=branch_data["name"],
                description=branch_data["description"],
                category=branch_data["category"],
                keywords=branch_data["keywords"],
                model_name=branch_data["model_name"],
                config=branch_data["config"],
                metadata=branch_data.get("metadata", {}),
            )

            self.logger.info(f"📥 Rama importada exitosamente: {branch_id}")
            return branch_id

        except Exception as e:
            self.logger.error(f"❌ Error importando rama: {e}")
            raise

    def get_base_domains(self) -> List[Dict[str, Any]]:
        """Obtener dominios base configurados"""
        return self.base_config.get("domains", [])

    def add_base_domain(self, name: str, keywords: List[str], description: str = ""):
        """Añadir nuevo dominio base"""
        new_domain = {"name": name, "keywords": keywords, "description": description}

        self.base_config["domains"].append(new_domain)

        with open(self.base_config_path, "w", encoding="utf-8") as f:
            json.dump(self.base_config, f, indent=2, ensure_ascii=False)

        self.logger.info(f"✅ Dominio base añadido: {name}")


# Instancia global del gestor de branches
branch_manager = BranchManager()
