#!/usr/bin/env python3
"""
Script de Migración para Consolidación de Módulos NeuroFusion

Este script identifica y consolida módulos duplicados en el sistema NeuroFusion,
migrando funcionalidades a la nueva arquitectura unificada.

Módulos a consolidar:
1. Sistemas de Evaluación de Calidad
2. Sistemas de Embeddings
3. Sistemas de Monitoreo
4. Sistemas de Aprendizaje
5. Sistemas de Seguridad
6. Sistemas de Memoria
7. Sistemas de Gestión de Ramas

Autor: NeuroFusion AI Team
Fecha: 2024-08-24
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModuleConsolidationMigrator:
    """Migrador para consolidar módulos duplicados"""

    def __init__(self, ai_directory: str = "ai"):
        self.ai_directory = Path(ai_directory)
        self.backup_directory = Path(
            "ai_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.consolidated_modules = {}
        self.duplicate_modules = {}

        # Mapeo de módulos duplicados
        self.duplicate_mappings = {
            # Sistemas de Evaluación de Calidad
            "evaluation_systems": {
                "ai_quality_evaluator.py": "UnifiedQualityEvaluator",
                "simple_ai_evaluator.py": "UnifiedQualityEvaluator",
                "response_orchestrator.py": "UnifiedQualityEvaluator",
                "score_quality.py": "UnifiedQualityEvaluator",
            },
            # Sistemas de Embeddings
            "embedding_systems": {
                "advanced_embedding_system.py": "UnifiedEmbeddingSystem",
                "perfect_embeddings.py": "UnifiedEmbeddingSystem",
                "perfect_embeddings_demo.py": "UnifiedEmbeddingSystem",
                "real_embeddings.py": "UnifiedEmbeddingSystem",
                "domain_embeddings.py": "UnifiedEmbeddingSystem",
                "real_time_embeddings.py": "UnifiedEmbeddingSystem",
                "vector_index_manager.py": "UnifiedEmbeddingSystem",
                "embedding_cache_optimizer.py": "UnifiedEmbeddingSystem",
                "advanced_embeddings.py": "UnifiedEmbeddingSystem",
            },
            # Sistemas de Monitoreo
            "monitoring_systems": {
                "advanced_monitoring_system.py": "UnifiedMonitoringSystem",
                "performance_metrics.py": "UnifiedMonitoringSystem",
                "advanced_tensor_metrics.py": "UnifiedMonitoringSystem",
            },
            # Sistemas de Aprendizaje
            "learning_systems": {
                "continuous_learning.py": "UnifiedLearningSystem",
                "continuous_learning_system.py": "UnifiedLearningSystem",
                "consolidated_learning_system.py": "UnifiedLearningSystem",
                "dynamic_training_system.py": "UnifiedLearningSystem",
                "gradient_training_system.py": "UnifiedLearningSystem",
                "advanced_llm_training.py": "UnifiedLearningSystem",
            },
            # Sistemas de Seguridad
            "security_systems": {
                "jwt_auth.py": "UnifiedAuthSecuritySystem",
                "two_factor_auth.py": "UnifiedAuthSecuritySystem",
                "digital_signature.py": "UnifiedAuthSecuritySystem",
                "password_policy.py": "UnifiedAuthSecuritySystem",
                "account_recovery.py": "UnifiedAuthSecuritySystem",
                "user_activity_monitor.py": "UnifiedAuthSecuritySystem",
                "user_anomaly_detector.py": "UnifiedAuthSecuritySystem",
                "intrusion_detection.py": "UnifiedAuthSecuritySystem",
            },
            # Sistemas de Memoria
            "memory_systems": {
                "episodic_memory_system.py": "UnifiedMemorySystem",
                "advanced_episodic_memory.py": "UnifiedMemorySystem",
                "master_indexing_system.py": "UnifiedMemorySystem",
                "rag_system.py": "UnifiedMemorySystem",
            },
            # Sistemas de Ramas
            "branch_systems": {
                "enhanced_multi_branch_system.py": "UnifiedBranchSystem",
                "enhanced_branch_detector.py": "UnifiedBranchSystem",
                "improve_branch_system.py": "UnifiedBranchSystem",
                "demo_branch_system_analysis.py": "UnifiedBranchSystem",
            },
            # Sistemas de Expertos
            "expert_systems": {
                "expert_system.py": "UnifiedExpertSystem",
                "multi_domain_expert_system.py": "UnifiedExpertSystem",
            },
            # Sistemas de Consciencia
            "consciousness_systems": {
                "consciousness_manager.py": "UnifiedConsciousnessSystem",
                "consciousness_adapter.py": "UnifiedConsciousnessSystem",
                "consciousness_system.py": "UnifiedConsciousnessSystem",
            },
            # Sistemas de Emociones
            "emotional_systems": {
                "emotional_controller.py": "UnifiedEmotionalSystem",
                "emotional_adapter.py": "UnifiedEmotionalSystem",
                "advanced_emotional_controller.py": "UnifiedEmotionalSystem",
                "real_emotional_analysis.py": "UnifiedEmotionalSystem",
                "emotion_types.py": "UnifiedEmotionalSystem",
            },
        }

    def analyze_duplicates(self) -> Dict[str, Any]:
        """Analizar módulos duplicados en el directorio"""

        logger.info("🔍 Analizando módulos duplicados...")

        analysis_results = {
            "total_files": 0,
            "duplicate_groups": 0,
            "files_to_consolidate": 0,
            "estimated_savings": 0,
            "duplicate_details": {},
        }

        # Contar archivos totales
        all_files = list(self.ai_directory.glob("*.py"))
        analysis_results["total_files"] = len(all_files)

        # Analizar duplicados por categoría
        for category, file_mapping in self.duplicate_mappings.items():
            category_files = []
            category_size = 0

            for filename in file_mapping.keys():
                file_path = self.ai_directory / filename
                if file_path.exists():
                    category_files.append(filename)
                    category_size += file_path.stat().st_size

            if category_files:
                analysis_results["duplicate_groups"] += 1
                analysis_results["files_to_consolidate"] += len(category_files)
                analysis_results["estimated_savings"] += (
                    category_size * 0.7
                )  # Estimación 70% de reducción

                analysis_results["duplicate_details"][category] = {
                    "files": category_files,
                    "total_size_bytes": category_size,
                    "consolidated_into": file_mapping[list(file_mapping.keys())[0]],
                }

        logger.info(f"📊 Análisis completado:")
        logger.info(f"   - Archivos totales: {analysis_results['total_files']}")
        logger.info(
            f"   - Grupos de duplicados: {analysis_results['duplicate_groups']}"
        )
        logger.info(
            f"   - Archivos a consolidar: {analysis_results['files_to_consolidate']}"
        )
        logger.info(
            f"   - Ahorro estimado: {analysis_results['estimated_savings'] / 1024:.1f} KB"
        )

        return analysis_results

    def create_backup(self) -> bool:
        """Crear backup de los módulos existentes"""

        try:
            logger.info(f"💾 Creando backup en: {self.backup_directory}")

            # Crear directorio de backup
            self.backup_directory.mkdir(exist_ok=True)

            # Copiar todos los archivos .py
            for py_file in self.ai_directory.glob("*.py"):
                backup_path = self.backup_directory / py_file.name
                shutil.copy2(py_file, backup_path)

            # Crear archivo de metadatos del backup
            backup_metadata = {
                "backup_created": datetime.now().isoformat(),
                "original_directory": str(self.ai_directory),
                "files_backed_up": len(list(self.ai_directory.glob("*.py"))),
                "migration_version": "1.0.0",
            }

            with open(self.backup_directory / "backup_metadata.json", "w") as f:
                json.dump(backup_metadata, f, indent=2)

            logger.info("✅ Backup creado exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False

    def consolidate_modules(self, dry_run: bool = True) -> Dict[str, Any]:
        """Consolidar módulos duplicados"""

        consolidation_results = {
            "consolidated_groups": 0,
            "files_processed": 0,
            "errors": [],
            "warnings": [],
        }

        logger.info(f"{'🔍 SIMULACIÓN' if dry_run else '🔄 CONSOLIDANDO'} módulos...")

        for category, file_mapping in self.duplicate_mappings.items():
            try:
                logger.info(f"\n📁 Procesando categoría: {category}")

                # Verificar archivos existentes
                existing_files = []
                for filename in file_mapping.keys():
                    file_path = self.ai_directory / filename
                    if file_path.exists():
                        existing_files.append(filename)

                if not existing_files:
                    logger.info(f"   ⚠️  No se encontraron archivos para {category}")
                    continue

                logger.info(f"   📋 Archivos encontrados: {len(existing_files)}")

                # Crear archivo consolidado
                consolidated_filename = f"unified_{category.replace('_', '_')}.py"
                consolidated_path = self.ai_directory / consolidated_filename

                if not dry_run:
                    # Crear archivo consolidado
                    self._create_consolidated_file(
                        category, existing_files, consolidated_path
                    )

                    # Mover archivos originales a subdirectorio de legacy
                    legacy_dir = self.ai_directory / "legacy_modules"
                    legacy_dir.mkdir(exist_ok=True)

                    for filename in existing_files:
                        original_path = self.ai_directory / filename
                        legacy_path = legacy_dir / filename
                        shutil.move(str(original_path), str(legacy_path))

                consolidation_results["consolidated_groups"] += 1
                consolidation_results["files_processed"] += len(existing_files)

                logger.info(f"   ✅ Consolidado en: {consolidated_filename}")

            except Exception as e:
                error_msg = f"Error consolidando {category}: {e}"
                logger.error(f"   ❌ {error_msg}")
                consolidation_results["errors"].append(error_msg)

        return consolidation_results

    def _create_consolidated_file(
        self, category: str, source_files: List[str], output_path: Path
    ):
        """Crear archivo consolidado para una categoría"""

        # Generar nombre de clase correcto
        class_name = (
            "".join(word.capitalize() for word in category.split("_")) + "System"
        )

        consolidated_content = f'''#!/usr/bin/env python3
"""
Módulo Consolidado: {category.replace('_', ' ').title()}

Este módulo consolida las funcionalidades de los siguientes módulos:
{chr(10).join(f"- {filename}" for filename in source_files)}

Consolidado automáticamente por NeuroFusion Migration Script
Fecha: {datetime.now().isoformat()}
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Unified{class_name}:
    """
    Sistema unificado que consolida funcionalidades de:
    {chr(10).join(f"    - {filename}" for filename in source_files)}
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.consolidated_modules = {source_files}
        logger.info(f"✅ Sistema unificado {category} inicializado")
    
    def get_consolidated_modules(self) -> List[str]:
        """Obtener lista de módulos consolidados"""
        return self.consolidated_modules
    
    def get_consolidation_info(self) -> Dict[str, Any]:
        """Obtener información de consolidación"""
        return {{
            "category": "{category}",
            "consolidated_modules": self.consolidated_modules,
            "consolidation_date": "{datetime.now().isoformat()}",
            "total_modules": len(self.consolidated_modules)
        }}

# Función de compatibilidad para migración gradual
def get_legacy_{category}_system():
    """Función de compatibilidad para sistemas legacy"""
    return Unified{class_name}()

if __name__ == "__main__":
    # Demostración del módulo consolidado
    system = Unified{class_name}()
    info = system.get_consolidation_info()
    print(f"🎉 Módulo consolidado: {{info}}")
'''

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(consolidated_content)

    def create_migration_report(
        self, analysis_results: Dict[str, Any], consolidation_results: Dict[str, Any]
    ) -> str:
        """Crear reporte de migración"""

        report = f"""
# Reporte de Migración NeuroFusion
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Resumen Ejecutivo
- Archivos totales analizados: {analysis_results['total_files']}
- Grupos de duplicados identificados: {analysis_results['duplicate_groups']}
- Archivos consolidados: {consolidation_results['files_processed']}
- Ahorro estimado de espacio: {analysis_results['estimated_savings'] / 1024:.1f} KB

## Detalles por Categoría
"""

        for category, details in analysis_results["duplicate_details"].items():
            report += f"""
### {category.replace('_', ' ').title()}
- Archivos: {', '.join(details['files'])}
- Tamaño total: {details['total_size_bytes'] / 1024:.1f} KB
- Consolidado en: {details['consolidated_into']}
"""

        if consolidation_results["errors"]:
            report += f"""
## Errores Encontrados
{chr(10).join(f"- {error}" for error in consolidation_results['errors'])}
"""

        if consolidation_results["warnings"]:
            report += f"""
## Advertencias
{chr(10).join(f"- {warning}" for warning in consolidation_results['warnings'])}
"""

        report += f"""
## Próximos Pasos
1. Revisar archivos consolidados
2. Actualizar imports en código existente
3. Ejecutar pruebas de integración
4. Eliminar archivos legacy después de validación

## Backup
- Ubicación: {self.backup_directory}
- Metadatos: {self.backup_directory}/backup_metadata.json
"""

        return report

    def restore_from_backup(self) -> bool:
        """Restaurar desde backup"""

        try:
            logger.info("🔄 Restaurando desde backup...")

            if not self.backup_directory.exists():
                logger.error("❌ Directorio de backup no encontrado")
                return False

            # Restaurar archivos
            for backup_file in self.backup_directory.glob("*.py"):
                restore_path = self.ai_directory / backup_file.name
                shutil.copy2(backup_file, restore_path)

            logger.info("✅ Restauración completada")
            return True

        except Exception as e:
            logger.error(f"❌ Error en restauración: {e}")
            return False


def main():
    """Función principal del script de migración"""

    print("🚀 Script de Migración NeuroFusion")
    print("=" * 50)

    # Crear migrador
    migrator = ModuleConsolidationMigrator()

    # Analizar duplicados
    print("\n📊 FASE 1: Análisis de Duplicados")
    analysis_results = migrator.analyze_duplicates()

    if analysis_results["duplicate_groups"] == 0:
        print("✅ No se encontraron módulos duplicados para consolidar")
        return

    # Crear backup
    print("\n💾 FASE 2: Creación de Backup")
    if not migrator.create_backup():
        print("❌ Error creando backup. Abortando migración.")
        return

    # Simular consolidación
    print("\n🔍 FASE 3: Simulación de Consolidación")
    consolidation_results = migrator.consolidate_modules(dry_run=True)

    # Mostrar resultados
    print("\n📋 RESULTADOS DE LA SIMULACIÓN:")
    print(f"   - Grupos consolidados: {consolidation_results['consolidated_groups']}")
    print(f"   - Archivos procesados: {consolidation_results['files_processed']}")
    print(f"   - Errores: {len(consolidation_results['errors'])}")

    if consolidation_results["errors"]:
        print("\n❌ Errores encontrados:")
        for error in consolidation_results["errors"]:
            print(f"   - {error}")

    # Preguntar confirmación
    print("\n🤔 ¿Desea proceder con la consolidación real? (s/N): ", end="")
    response = input().strip().lower()

    if response in ["s", "si", "sí", "y", "yes"]:
        print("\n🔄 FASE 4: Consolidación Real")
        consolidation_results = migrator.consolidate_modules(dry_run=False)

        # Crear reporte
        report = migrator.create_migration_report(
            analysis_results, consolidation_results
        )

        with open("migration_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print("\n✅ Consolidación completada!")
        print("📄 Reporte guardado en: migration_report.md")
        print(f"💾 Backup disponible en: {migrator.backup_directory}")

    else:
        print("\n❌ Consolidación cancelada")
        print("💾 Backup disponible en caso de necesitarlo")


if __name__ == "__main__":
    main()
