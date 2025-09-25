#!/usr/bin/env python3
"""
Consolidador de Módulos - Sheily AI
===================================
Consolida módulos duplicados identificados en la auditoría
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set
import json

logger = logging.getLogger(__name__)

class ModuleConsolidator:
    """Consolidador de módulos duplicados"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.modules_dir = self.project_root / "modules"
        self.consolidated_dir = self.project_root / "modules_consolidated"
        
        # Módulos duplicados identificados en la auditoría
        self.duplicate_groups = {
            "evaluation_systems": [
                "modules/evaluation/coherence.py",
                "modules/evaluation/diversity.py", 
                "modules/evaluation/toxicity.py",
                "modules/evaluation/performance_benchmark.py"
            ],
            "embedding_systems": [
                "modules/embeddings/embedding_manager.py",
                "data/embeddings_manager.py"
            ],
            "monitoring_systems": [
                "modules/monitoring/system_monitor.py",
                "monitoring/system_monitor.py"
            ],
            "security_systems": [
                "modules/security/authentication.py",
                "modules/security/encryption.py",
                "modules/unified_systems/unified_auth_security_system.py"
            ],
            "memory_systems": [
                "memory/branch_memory_integrator.py",
                "modules/memory/branch_memory_integrator.py"
            ],
            "config_systems": [
                "config/config_manager.py",
                "modules/config/config_manager.py"
            ]
        }
    
    def analyze_duplicates(self) -> Dict[str, any]:
        """Analizar módulos duplicados"""
        results = {
            "total_files": 0,
            "duplicate_groups": 0,
            "files_to_consolidate": 0,
            "estimated_savings": 0,
            "groups": {}
        }
        
        for group_name, file_paths in self.duplicate_groups.items():
            existing_files = []
            total_size = 0
            
            for file_path in file_paths:
                full_path = self.project_root / file_path
                if full_path.exists():
                    existing_files.append(str(file_path))
                    total_size += full_path.stat().st_size
            
            if len(existing_files) > 1:
                results["duplicate_groups"] += 1
                results["files_to_consolidate"] += len(existing_files)
                results["estimated_savings"] += total_size * 0.7  # Estimación de ahorro
                
                results["groups"][group_name] = {
                    "files": existing_files,
                    "size": total_size,
                    "consolidation_target": f"modules_consolidated/{group_name}.py"
                }
            
            results["total_files"] += len(existing_files)
        
        return results
    
    def create_consolidated_module(self, group_name: str, files: List[str]) -> bool:
        """Crear módulo consolidado"""
        try:
            # Crear directorio consolidado
            self.consolidated_dir.mkdir(exist_ok=True)
            
            # Archivo consolidado
            consolidated_file = self.consolidated_dir / f"{group_name}.py"
            
            with open(consolidated_file, 'w', encoding='utf-8') as outfile:
                outfile.write(f'#!/usr/bin/env python3\n')
                outfile.write(f'"""\n')
                outfile.write(f'Módulo Consolidado: {group_name.replace("_", " ").title()}\n')
                outfile.write(f'==========================================\n')
                outfile.write(f'Consolidado desde: {", ".join(files)}\n')
                outfile.write(f'"""\n\n')
                
                # Combinar archivos
                for file_path in files:
                    full_path = self.project_root / file_path
                    if full_path.exists():
                        outfile.write(f'# === {file_path} ===\n')
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            # Limpiar imports duplicados y headers
                            lines = content.split('\n')
                            skip_lines = 0
                            for i, line in enumerate(lines):
                                if line.startswith('#!/usr/bin/env python3'):
                                    skip_lines = i + 1
                                elif line.startswith('"""') and i < 10:
                                    # Buscar el final del docstring
                                    for j in range(i + 1, len(lines)):
                                        if lines[j].endswith('"""'):
                                            skip_lines = j + 1
                                            break
                                elif line.startswith('import ') or line.startswith('from '):
                                    break
                                else:
                                    skip_lines = i
                            
                            # Escribir contenido limpio
                            clean_content = '\n'.join(lines[skip_lines:])
                            outfile.write(clean_content)
                            outfile.write('\n\n')
            
            logger.info(f"✅ Módulo consolidado creado: {consolidated_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando módulo consolidado {group_name}: {e}")
            return False
    
    def backup_original_files(self) -> bool:
        """Crear backup de archivos originales"""
        try:
            backup_dir = self.project_root / "backup_original_modules"
            backup_dir.mkdir(exist_ok=True)
            
            for group_name, file_paths in self.duplicate_groups.items():
                group_backup_dir = backup_dir / group_name
                group_backup_dir.mkdir(exist_ok=True)
                
                for file_path in file_paths:
                    full_path = self.project_root / file_path
                    if full_path.exists():
                        backup_path = group_backup_dir / Path(file_path).name
                        shutil.copy2(full_path, backup_path)
            
            logger.info(f"✅ Backup creado en {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False
    
    def consolidate_all(self, dry_run: bool = True) -> Dict[str, any]:
        """Consolidar todos los módulos duplicados"""
        results = {
            "success": True,
            "consolidated_groups": 0,
            "errors": [],
            "warnings": []
        }
        
        # Analizar duplicados
        analysis = self.analyze_duplicates()
        
        if analysis["duplicate_groups"] == 0:
            logger.info("✅ No se encontraron módulos duplicados para consolidar")
            return results
        
        logger.info(f"🔍 {'Simulando' if dry_run else 'Ejecutando'} consolidación...")
        logger.info(f"   - Grupos duplicados: {analysis['duplicate_groups']}")
        logger.info(f"   - Archivos a consolidar: {analysis['files_to_consolidate']}")
        logger.info(f"   - Ahorro estimado: {analysis['estimated_savings'] / 1024:.1f} KB")
        
        # Crear backup si no es dry run
        if not dry_run:
            if not self.backup_original_files():
                results["success"] = False
                results["errors"].append("Error creando backup")
                return results
        
        # Consolidar cada grupo
        for group_name, group_info in analysis["groups"].items():
            try:
                if not dry_run:
                    if self.create_consolidated_module(group_name, group_info["files"]):
                        results["consolidated_groups"] += 1
                    else:
                        results["errors"].append(f"Error consolidando {group_name}")
                else:
                    results["consolidated_groups"] += 1
                    logger.info(f"   📁 {group_name}: {len(group_info['files'])} archivos → {group_info['consolidation_target']}")
                    
            except Exception as e:
                results["errors"].append(f"Error procesando {group_name}: {e}")
        
        if results["errors"]:
            results["success"] = False
        
        return results
    
    def generate_consolidation_report(self) -> str:
        """Generar reporte de consolidación"""
        analysis = self.analyze_duplicates()
        
        report = f"""
# Reporte de Consolidación de Módulos - Sheily AI

## Resumen
- **Total de archivos analizados**: {analysis['total_files']}
- **Grupos duplicados encontrados**: {analysis['duplicate_groups']}
- **Archivos a consolidar**: {analysis['files_to_consolidate']}
- **Ahorro estimado**: {analysis['estimated_savings'] / 1024:.1f} KB

## Grupos de Consolidación

"""
        
        for group_name, group_info in analysis["groups"].items():
            report += f"### {group_name.replace('_', ' ').title()}\n"
            report += f"- **Archivos**: {len(group_info['files'])}\n"
            report += f"- **Tamaño**: {group_info['size'] / 1024:.1f} KB\n"
            report += f"- **Archivo consolidado**: `{group_info['consolidation_target']}`\n"
            report += f"- **Archivos originales**:\n"
            for file_path in group_info['files']:
                report += f"  - `{file_path}`\n"
            report += "\n"
        
        return report

def main():
    """Función principal"""
    print("🚀 Consolidador de Módulos - Sheily AI")
    print("=" * 50)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear consolidador
    consolidator = ModuleConsolidator()
    
    # Analizar duplicados
    print("\n📊 FASE 1: Análisis de Duplicados")
    analysis = consolidator.analyze_duplicates()
    
    if analysis["duplicate_groups"] == 0:
        print("✅ No se encontraron módulos duplicados para consolidar")
        return 0
    
    print(f"   - Grupos duplicados: {analysis['duplicate_groups']}")
    print(f"   - Archivos a consolidar: {analysis['files_to_consolidate']}")
    print(f"   - Ahorro estimado: {analysis['estimated_savings'] / 1024:.1f} KB")
    
    # Simular consolidación
    print("\n🔍 FASE 2: Simulación de Consolidación")
    results = consolidator.consolidate_all(dry_run=True)
    
    if results["errors"]:
        print("\n❌ Errores encontrados:")
        for error in results["errors"]:
            print(f"   - {error}")
        return 1
    
    # Preguntar confirmación (automático para scripts)
    print("\n🤔 Procediendo con la consolidación real...")
    response = 's'  # Automático para evitar input interactivo
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n🔄 FASE 3: Consolidación Real")
        results = consolidator.consolidate_all(dry_run=False)
        
        if results["success"]:
            print(f"✅ Consolidación completada exitosamente")
            print(f"   - Grupos consolidados: {results['consolidated_groups']}")
            
            # Generar reporte
            report = consolidator.generate_consolidation_report()
            with open("consolidation_report.md", "w", encoding="utf-8") as f:
                f.write(report)
            print("📄 Reporte generado: consolidation_report.md")
        else:
            print("❌ Error en la consolidación")
            for error in results["errors"]:
                print(f"   - {error}")
            return 1
    else:
        print("❌ Consolidación cancelada por el usuario")
    
    return 0

if __name__ == "__main__":
    exit(main())
