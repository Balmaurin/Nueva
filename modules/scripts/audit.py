#!/usr/bin/env python3
"""
Script de Auditoría de Modelos de Sheily AI
===========================================

Este script audita y verifica el estado de los dos modelos principales:
- Modelo Principal: Sheily Personal Model (4-bit)
- Modelo de Ramas: paraphrase-multilingual-MiniLM-L12-v2 (16-bit)
"""

import os
import sys
import json
import logging
import torch
from pathlib import Path
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelAuditor:
    """
    Auditor de modelos para Shaili AI

    Verifica:
    - Estado de los modelos principales
    - Configuraciones de cuantización
    - Integridad de archivos
    - Rendimiento y memoria
    """

    def __init__(self):
        """Inicializar auditor"""
        self.audit_results = {}
        self.issues = []
        self.warnings = []

    def audit_main_model(self) -> Dict[str, Any]:
        """
        Auditar el modelo principal (Shaili Personal Model)

        Returns:
            Dict[str, Any]: Resultados de la auditoría
        """
        logger.info("🔍 Auditar modelo principal: Shaili Personal Model")

        results = {
            "model_name": "Shaili Personal Model",
            "model_path": "models/custom/shaili-personal-model",
            "quantization": "4-bit",
            "status": "UNKNOWN",
            "issues": [],
            "warnings": [],
            "files": {},
            "performance": {},
        }

        model_path = Path(results["model_path"])

        # Verificar existencia del directorio
        if not model_path.exists():
            results["status"] = "MISSING"
            results["issues"].append("Directorio del modelo no encontrado")
            return results

        # Verificar archivos necesarios
        required_files = [
            "config.json",
            "pytorch_model.bin",
            "tokenizer.json",
            "tokenizer_config.json",
        ]

        for file in required_files:
            file_path = model_path / file
            if file_path.exists():
                size = file_path.stat().st_size
                results["files"][file] = {
                    "exists": True,
                    "size_mb": round(size / (1024 * 1024), 2),
                }
            else:
                results["files"][file] = {"exists": False, "size_mb": 0}
                results["issues"].append(f"Archivo faltante: {file}")

        # Verificar configuración de cuantización
        quant_config_path = model_path / "quantization_config.json"
        if quant_config_path.exists():
            try:
                with open(quant_config_path, "r") as f:
                    quant_config = json.load(f)
                results["quantization_config"] = quant_config
            except Exception as e:
                results["warnings"].append(
                    f"Error leyendo configuración de cuantización: {e}"
                )
        else:
            results["warnings"].append("Configuración de cuantización no encontrada")

        # Intentar cargar el modelo
        try:
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from modules.core.model.shaili_model import ShailiBaseModel

            model = ShailiBaseModel(model_id=str(model_path), quantization="4bit")

            results["status"] = "LOADED"
            results["performance"]["device"] = str(model.base_model.device)
            results["performance"]["dtype"] = str(model.base_model.dtype)

            # Verificar parámetros
            total_params = sum(p.numel() for p in model.base_model.parameters())
            results["performance"]["total_parameters"] = total_params

            logger.info(f"✅ Modelo principal cargado correctamente")

        except Exception as e:
            results["status"] = "ERROR"
            results["issues"].append(f"Error cargando modelo: {str(e)}")
            logger.error(f"❌ Error cargando modelo principal: {e}")

        return results

    def audit_branch_model(self) -> Dict[str, Any]:
        """
        Auditar el modelo de ramas (paraphrase-multilingual-MiniLM-L12-v2)

        Returns:
            Dict[str, Any]: Resultados de la auditoría
        """
        logger.info("🔍 Auditar modelo de ramas: paraphrase-multilingual-MiniLM-L12-v2")

        results = {
            "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
            "model_path": "models/custom/shaili-personal-model",
            "quantization": "16-bit",
            "status": "UNKNOWN",
            "issues": [],
            "warnings": [],
            "files": {},
            "performance": {},
        }

        model_path = Path(results["model_path"])

        # Verificar existencia del directorio
        if not model_path.exists():
            results["status"] = "MISSING"
            results["issues"].append("Directorio del modelo no encontrado")
            return results

        # Verificar archivos necesarios para modelo principal
        required_files = [
            "config.json",
            "model.safetensors.index.json",
            "tokenizer.json",
            "tokenizer_config.json",
        ]

        for file in required_files:
            file_path = model_path / file
            if file_path.exists():
                size = file_path.stat().st_size
                results["files"][file] = {
                    "exists": True,
                    "size_mb": round(size / (1024 * 1024), 2),
                }
            else:
                results["files"][file] = {"exists": False, "size_mb": 0}
                if file in ["config.json", "pytorch_model.bin"]:
                    results["issues"].append(f"Archivo faltante: {file}")
                else:
                    results["warnings"].append(f"Archivo opcional faltante: {file}")

        # Intentar cargar el modelo
        try:
            from transformers import AutoModel, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model = AutoModel.from_pretrained(str(model_path))

            results["status"] = "LOADED"
            results["performance"]["embedding_dim"] = model.config.hidden_size
            results["performance"][
                "max_seq_length"
            ] = model.config.max_position_embeddings

            # Probar generación de embeddings
            test_text = "Texto de prueba para verificar embeddings"
            inputs = tokenizer(
                test_text, return_tensors="pt", padding=True, truncation=True
            )
            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                results["performance"]["test_embedding_shape"] = list(embeddings.shape)

            logger.info(f"✅ Modelo de ramas cargado correctamente")

        except Exception as e:
            results["status"] = "ERROR"
            results["issues"].append(f"Error cargando modelo: {str(e)}")
            logger.error(f"❌ Error cargando modelo de ramas: {e}")

        return results

    def audit_system_integration(self) -> Dict[str, Any]:
        """
        Auditar la integración del sistema

        Returns:
            Dict[str, Any]: Resultados de la auditoría
        """
        logger.info("🔍 Auditar integración del sistema")

        results = {
            "integration_status": "UNKNOWN",
            "components": {},
            "issues": [],
            "warnings": [],
        }

        # Verificar gestor de ramas
        try:
            from models.branches.branch_manager import BranchManager

            branch_manager = BranchManager()
            results["components"]["branch_manager"] = "LOADED"

        except Exception as e:
            results["components"]["branch_manager"] = "ERROR"
            results["issues"].append(f"Error cargando gestor de ramas: {str(e)}")

        # Verificar modelo simple
        try:
            from modules.core.model.simple_shaili import SimpleShailiModel

            simple_model = SimpleShailiModel()
            results["components"]["simple_model"] = "LOADED"

        except Exception as e:
            results["components"]["simple_model"] = "ERROR"
            results["issues"].append(f"Error cargando modelo simple: {str(e)}")

        # Verificar base de datos
        db_path = Path("models/branch_learning.db")
        if db_path.exists():
            results["components"]["database"] = "EXISTS"
        else:
            results["components"]["database"] = "MISSING"
            results["warnings"].append("Base de datos de ramas no encontrada")

        # Determinar estado general
        if any(status == "ERROR" for status in results["components"].values()):
            results["integration_status"] = "ERROR"
        elif any(status == "MISSING" for status in results["components"].values()):
            results["integration_status"] = "WARNING"
        else:
            results["integration_status"] = "OK"

        return results

    def audit_memory_usage(self) -> Dict[str, Any]:
        """
        Auditar uso de memoria

        Returns:
            Dict[str, Any]: Resultados de la auditoría
        """
        logger.info("🔍 Auditar uso de memoria")

        results = {
            "memory_status": "UNKNOWN",
            "gpu_available": torch.cuda.is_available(),
            "memory_usage": {},
            "warnings": [],
        }

        if torch.cuda.is_available():
            results["memory_usage"]["gpu_total"] = round(
                torch.cuda.get_device_properties(0).total_memory / (1024**3), 2
            )
            results["memory_usage"]["gpu_allocated"] = round(
                torch.cuda.memory_allocated(0) / (1024**3), 2
            )
            results["memory_usage"]["gpu_cached"] = round(
                torch.cuda.memory_reserved(0) / (1024**3), 2
            )

            # Verificar si hay suficiente memoria para los modelos
            if results["memory_usage"]["gpu_total"] < 4:
                results["warnings"].append("GPU con poca memoria (< 4GB)")
        else:
            results["warnings"].append("GPU no disponible, usando CPU")

        return results

    def run_full_audit(self) -> Dict[str, Any]:
        """
        Ejecutar auditoría completa

        Returns:
            Dict[str, Any]: Resultados completos de la auditoría
        """
        logger.info("🚀 Iniciando auditoría completa del sistema")

        audit_results = {
            "timestamp": str(torch.datetime.now()),
            "main_model": self.audit_main_model(),
            "branch_model": self.audit_branch_model(),
            "system_integration": self.audit_system_integration(),
            "memory_usage": self.audit_memory_usage(),
            "summary": {},
        }

        # Generar resumen
        main_status = audit_results["main_model"]["status"]
        branch_status = audit_results["branch_model"]["status"]
        integration_status = audit_results["system_integration"]["integration_status"]

        if (
            main_status == "LOADED"
            and branch_status == "LOADED"
            and integration_status == "OK"
        ):
            audit_results["summary"]["overall_status"] = "HEALTHY"
            audit_results["summary"][
                "message"
            ] = "Todos los modelos funcionando correctamente"
        elif main_status == "LOADED" and branch_status == "LOADED":
            audit_results["summary"]["overall_status"] = "WARNING"
            audit_results["summary"][
                "message"
            ] = "Modelos cargados pero problemas de integración"
        else:
            audit_results["summary"]["overall_status"] = "CRITICAL"
            audit_results["summary"]["message"] = "Problemas críticos con los modelos"

        return audit_results

    def generate_report(self, audit_results: Dict[str, Any]) -> str:
        """
        Generar reporte de auditoría

        Args:
            audit_results (Dict[str, Any]): Resultados de la auditoría

        Returns:
            str: Reporte formateado
        """
        report = []
        report.append("=" * 80)
        report.append("REPORTE DE AUDITORÍA - SHAILI AI")
        report.append("=" * 80)
        report.append(f"Fecha: {audit_results['timestamp']}")
        report.append("")

        # Resumen general
        summary = audit_results["summary"]
        report.append(f"ESTADO GENERAL: {summary['overall_status']}")
        report.append(f"Mensaje: {summary['message']}")
        report.append("")

        # Modelo principal
        main = audit_results["main_model"]
        report.append("📊 MODELO PRINCIPAL (Shaili Personal Model)")
        report.append(f"   Estado: {main['status']}")
        report.append(f"   Cuantización: {main['quantization']}")

        if main["files"]:
            report.append("   Archivos:")
            for file, info in main["files"].items():
                if info["exists"]:
                    report.append(f"     ✅ {file} ({info['size_mb']} MB)")
                else:
                    report.append(f"     ❌ {file} (FALTANTE)")

        if main["issues"]:
            report.append("   Problemas:")
            for issue in main["issues"]:
                report.append(f"     ❌ {issue}")

        report.append("")

        # Modelo de ramas
        branch = audit_results["branch_model"]
        report.append("🔍 MODELO DE RAMAS (paraphrase-multilingual-MiniLM-L12-v2)")
        report.append(f"   Estado: {branch['status']}")
        report.append(f"   Cuantización: {branch['quantization']}")

        if branch["performance"]:
            report.append("   Rendimiento:")
            for key, value in branch["performance"].items():
                report.append(f"     {key}: {value}")

        if branch["issues"]:
            report.append("   Problemas:")
            for issue in branch["issues"]:
                report.append(f"     ❌ {issue}")

        report.append("")

        # Integración del sistema
        integration = audit_results["system_integration"]
        report.append("🔧 INTEGRACIÓN DEL SISTEMA")
        report.append(f"   Estado: {integration['integration_status']}")

        for component, status in integration["components"].items():
            if status == "LOADED":
                report.append(f"     ✅ {component}: {status}")
            elif status == "EXISTS":
                report.append(f"     ✅ {component}: {status}")
            else:
                report.append(f"     ❌ {component}: {status}")

        report.append("")

        # Uso de memoria
        memory = audit_results["memory_usage"]
        report.append("💾 USO DE MEMORIA")
        report.append(f"   GPU disponible: {memory['gpu_available']}")

        if memory["gpu_available"]:
            for key, value in memory["memory_usage"].items():
                report.append(f"   {key}: {value} GB")

        if memory["warnings"]:
            report.append("   Advertencias:")
            for warning in memory["warnings"]:
                report.append(f"     ⚠️ {warning}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Función principal de auditoría"""
    logger.info("🚀 Iniciando auditoría de modelos de Shaili AI")

    auditor = ModelAuditor()

    # Ejecutar auditoría completa
    results = auditor.run_full_audit()

    # Generar y mostrar reporte
    report = auditor.generate_report(results)
    print(report)

    # Guardar reporte en archivo
    report_path = "audit_report.txt"
    with open(report_path, "w") as f:
        f.write(report)

    logger.info(f"📄 Reporte guardado en: {report_path}")

    # Retornar código de salida según el estado
    if results["summary"]["overall_status"] == "HEALTHY":
        logger.info("✅ Auditoría completada - Sistema saludable")
        return 0
    elif results["summary"]["overall_status"] == "WARNING":
        logger.warning("⚠️ Auditoría completada - Advertencias encontradas")
        return 1
    else:
        logger.error("❌ Auditoría completada - Problemas críticos")
        return 2


if __name__ == "__main__":
    exit(main())
