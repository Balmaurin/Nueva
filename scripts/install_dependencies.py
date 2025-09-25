#!/usr/bin/env python3
"""
Script de instalación de dependencias para NeuroFusion
"""

import subprocess
import sys
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_requirements():
    """
    Actualizar archivo requirements.txt con nuevas dependencias
    """
    try:
        with open("requirements.txt", "a") as f:
            f.write("\n# Dependencias adicionales\n")
            f.write("duckdb\n")
            f.write("astor\n")
            f.write("radon\n")
            f.write("pyinstrument\n")
            f.write("plotly\n")
            f.write("beautifulsoup4\n")
            f.write("mlflow\n")
            f.write("gitpython\n")
        logger.info("✅ requirements.txt actualizado")
    except Exception as e:
        logger.error(f"❌ Error actualizando requirements.txt: {e}")


def install_dependencies():
    """
    Instalar dependencias faltantes para NeuroFusion
    """
    dependencies = [
        # Bases de datos y almacenamiento
        "duckdb",
        # Herramientas de análisis y transformación de código
        "astor",
        "radon",
        "pyinstrument",
        # Visualización
        "plotly",
        # Procesamiento de HTML/Web scraping
        "beautifulsoup4",  # Reemplazo de bs4
        # Herramientas de tracking
        "mlflow",  # Reemplazo de tracker genérico
        # Herramientas de manejo de ramas y versiones
        "gitpython",  # Reemplazo de branches
    ]

    failed_dependencies = []

    for dep in dependencies:
        try:
            logger.info(f"Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            logger.info(f"✅ {dep} instalado exitosamente")
        except subprocess.CalledProcessError:
            logger.error(f"❌ Error instalando {dep}")
            failed_dependencies.append(dep)

    if failed_dependencies:
        logger.warning("Las siguientes dependencias no pudieron instalarse:")
        for dep in failed_dependencies:
            logger.warning(f"- {dep}")
        return False

    return True


def main():
    """
    Punto de entrada principal
    """
    logger.info("🚀 Iniciando instalación de dependencias para NeuroFusion")

    success = install_dependencies()

    if success:
        update_requirements()
        logger.info("✨ Instalación de dependencias completada")
        return {"status": "ok", "message": "Dependencias instaladas exitosamente"}
    else:
        logger.error("❌ Instalación de dependencias incompleta")
        return {
            "status": "error",
            "message": "Algunas dependencias no pudieron instalarse",
        }


if __name__ == "__main__":
    result = main()
    print(result)
