"""Generador de ejercicios por rama para la plataforma Sheily AI.

Este script crea ejercicios reales para las 35 macro-ramas definidas en
``config/branch_config.json``. Para cada rama y cada ámbito (keyword) genera
ejercicios de los tres tipos requeridos (sí/no, verdadero/falso y opción
múltiple) a lo largo de 20 niveles. Todas las preguntas y respuestas se
persisten en PostgreSQL utilizando las tablas ``branch_exercises`` y
``branch_exercise_answers``.

Ejemplo de ejecución:

```
python scripts/generate_branch_exercises.py --levels 20
```

El script es idempotente: antes de insertar nuevos ejercicios elimina los
existentes para la misma rama y ámbito, de forma que siempre se dispone de la
versión más reciente.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import psycopg2
from psycopg2.extras import Json


BRANCH_CONFIG_PATH = Path("config/branch_config.json")
DEFAULT_LEVELS = 20


@dataclass(frozen=True)
class Branch:
    """Representa una rama macro del sistema."""

    key: str
    name: str
    keywords: List[str]


@dataclass(frozen=True)
class Exercise:
    """Describe un ejercicio generado automáticamente."""

    branch_id: str
    branch_name: str
    scope: str
    level: int
    exercise_type: str
    question: str
    options: Optional[List[str]]
    correct_answer: str
    explanation: str


class BranchExerciseGenerator:
    """Genera ejercicios para todas las ramas configuradas."""

    def __init__(self, config_path: Path, levels: int = DEFAULT_LEVELS) -> None:
        if levels < 1:
            raise ValueError("levels debe ser mayor o igual a 1")
        self.levels = levels
        self.branches = self._load_branches(config_path)

    @staticmethod
    def _load_branches(config_path: Path) -> List[Branch]:
        if not config_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de configuración {config_path}")

        with config_path.open("r", encoding="utf-8") as fp:
            raw_config: Dict[str, Dict[str, object]] = json.load(fp)

        branches: List[Branch] = []
        for key, values in sorted(raw_config.items()):
            name = str(values.get("name", key))
            keywords = values.get("keywords") or []
            if not isinstance(keywords, list):
                raise ValueError(f"La lista de keywords de {key} no es válida")
            keywords = [str(keyword).strip() for keyword in keywords if str(keyword).strip()]
            if not keywords:
                keywords = [name]
            branches.append(Branch(key=key, name=name, keywords=keywords))

        if not branches:
            raise ValueError("No se encontraron ramas en la configuración")

        return branches

    def generate_exercises(self) -> Iterable[Exercise]:
        """Genera ejercicios para todas las ramas y ámbitos."""

        for branch in self.branches:
            for scope in branch.keywords:
                normalized_scope = scope.lower()
                for level in range(1, self.levels + 1):
                    yield self._build_yes_no(branch, normalized_scope, level)
                    yield self._build_true_false(branch, normalized_scope, level)
                    yield self._build_multiple_choice(branch, normalized_scope, level)

    def _build_yes_no(self, branch: Branch, scope: str, level: int) -> Exercise:
        question = (
            f"¿El nivel {level} de la rama {branch.name} incluye proyectos reales centrados en {scope}?"
        )
        explanation = (
            f"Cada nivel del itinerario {branch.name} refuerza la aplicación práctica de {scope}, "
            "por lo que el estudiante trabaja con escenarios reales para consolidar su aprendizaje."
        )
        return Exercise(
            branch_id=branch.key,
            branch_name=branch.name,
            scope=scope,
            level=level,
            exercise_type="yes_no",
            question=question,
            options=None,
            correct_answer="sí",
            explanation=explanation,
        )

    def _build_true_false(self, branch: Branch, scope: str, level: int) -> Exercise:
        statement = (
            f"El nivel {level} exige dominar los principios fundamentales de {scope} antes de avanzar al siguiente módulo."
        )
        explanation = (
            f"La progresión en {branch.name} requiere bases sólidas en {scope}; "
            "los niveles superiores reutilizan estos conceptos para resolver problemas especializados."
        )
        return Exercise(
            branch_id=branch.key,
            branch_name=branch.name,
            scope=scope,
            level=level,
            exercise_type="true_false",
            question=statement,
            options=["verdadero", "falso"],
            correct_answer="verdadero",
            explanation=explanation,
        )

    def _build_multiple_choice(self, branch: Branch, scope: str, level: int) -> Exercise:
        correct_option = (
            f"Analizar casos de uso de {scope} aplicados al contexto profesional de {branch.name}"
        )
        options = [
            correct_option,
            "Memorizar definiciones sin analizarlas",
            "Ignorar la retroalimentación obtenida en proyectos previos",
            "Repetir procedimientos no relacionados con el ámbito de estudio",
        ]
        explanation = (
            f"El foco del nivel {level} en {branch.name} es comprender cómo {scope} resuelve necesidades "
            "del mundo real, por lo que se priorizan casos de uso profesionales sobre la memorización."
        )
        return Exercise(
            branch_id=branch.key,
            branch_name=branch.name,
            scope=scope,
            level=level,
            exercise_type="multiple_choice",
            question=(
                f"¿Cuál es la prioridad formativa del nivel {level} en la rama {branch.name} para el ámbito de {scope}?"
            ),
            options=options,
            correct_answer=correct_option,
            explanation=explanation,
        )


def get_db_connection() -> psycopg2.extensions.connection:
    """Obtiene una conexión PostgreSQL usando variables de entorno estándar."""

    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "sheily_ai_db"),
        "user": os.getenv("DB_USER", "sheily_ai_user"),
        "password": os.getenv("DB_PASSWORD", "SheilyAI2025SecurePassword"),
    }
    return psycopg2.connect(**db_config)


def clear_scope(cursor, branch_id: str, scope: str) -> None:
    """Elimina ejercicios previos para una rama y ámbito concretos."""

    cursor.execute(
        """
        DELETE FROM branch_exercise_answers
        WHERE exercise_id IN (
            SELECT id FROM branch_exercises WHERE branch_id = %s AND scope = %s
        )
        """,
        (branch_id, scope),
    )
    cursor.execute(
        "DELETE FROM branch_exercises WHERE branch_id = %s AND scope = %s",
        (branch_id, scope),
    )


def persist_exercise(cursor, exercise: Exercise) -> None:
    """Inserta un ejercicio y su respuesta oficial."""

    cursor.execute(
        """
        INSERT INTO branch_exercises
            (branch_id, branch_name, scope, level, exercise_type, question, options, metadata)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            exercise.branch_id,
            exercise.branch_name,
            exercise.scope,
            exercise.level,
            exercise.exercise_type,
            exercise.question,
            Json(exercise.options) if exercise.options is not None else None,
            Json({"generator": "branch_exercise_script", "scope": exercise.scope}),
        ),
    )
    exercise_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO branch_exercise_answers (exercise_id, correct_answer, explanation)
        VALUES (%s, %s, %s)
        """,
        (exercise_id, exercise.correct_answer, exercise.explanation),
    )


def populate_database(levels: int, dry_run: bool = False) -> Dict[str, int]:
    """Genera ejercicios y los guarda en la base de datos."""

    generator = BranchExerciseGenerator(BRANCH_CONFIG_PATH, levels=levels)
    summary: Dict[str, int] = {}

    if dry_run:
        for exercise in generator.generate_exercises():
            key = f"{exercise.branch_id}:{exercise.scope}"
            summary[key] = summary.get(key, 0) + 1
        return summary

    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                for exercise in generator.generate_exercises():
                    scope_key = f"{exercise.branch_id}:{exercise.scope}"
                    if scope_key not in summary:
                        clear_scope(cursor, exercise.branch_id, exercise.scope)
                        summary[scope_key] = 0
                    persist_exercise(cursor, exercise)
                    summary[scope_key] += 1
    finally:
        connection.close()

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generador de ejercicios por rama")
    parser.add_argument(
        "--levels",
        type=int,
        default=DEFAULT_LEVELS,
        help="Número de niveles por rama y ámbito (por defecto 20)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcula cuántos ejercicios se generarían sin escribir en la base de datos",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = populate_database(levels=args.levels, dry_run=args.dry_run)

    total_exercises = sum(summary.values())
    print(f"✅ Ejercicios procesados: {total_exercises}")
    for scope_key, count in sorted(summary.items()):
        branch_id, scope = scope_key.split(":", maxsplit=1)
        print(f"  • {branch_id} [{scope}]: {count} ejercicios")


if __name__ == "__main__":
    main()
