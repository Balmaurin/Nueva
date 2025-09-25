"""
Utilidades Generales de Modelos
==============================

Este módulo proporciona utilidades generales para el sistema de modelos.
"""

import os
import json
import logging
import hashlib
import shutil
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import torch
from models.utils.device_utils import DeviceUtils
from models.utils.memory_utils import MemoryManager


class ModelUtils:
    """
    Utilidades generales para modelos

    Proporciona:
    - Validación de modelos
    - Gestión de archivos
    - Conversiones de formato
    - Utilidades de hash y verificación
    """

    def __init__(self):
        """Inicializar utilidades de modelos"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_utils = DeviceUtils()
        self.memory_manager = MemoryManager()

    def validate_model_path(self, model_path: str) -> Dict[str, Any]:
        """
        Validar ruta de modelo

        Args:
            model_path: Ruta del modelo

        Returns:
            Dict: Resultado de la validación
        """
        result = {
            "valid": False,
            "exists": False,
            "is_directory": False,
            "has_config": False,
            "has_model_files": False,
            "errors": [],
        }

        try:
            path = Path(model_path)

            # Verificar si existe
            if not path.exists():
                result["errors"].append("La ruta no existe")
                return result

            result["exists"] = True

            # Verificar si es directorio
            if not path.is_dir():
                result["errors"].append("La ruta no es un directorio")
                return result

            result["is_directory"] = True

            # Verificar archivos de configuración
            config_files = [
                "config.json",
                "model_config.json",
                "generation_config.json",
            ]
            has_config = any(
                (path / config_file).exists() for config_file in config_files
            )
            result["has_config"] = has_config

            if not has_config:
                result["errors"].append("No se encontraron archivos de configuración")

            # Verificar archivos de modelo
            model_files = [
                "pytorch_model.bin",
                "model.safetensors",
                "model-00001-of-00001.safetensors",
            ]
            has_model_files = any(
                (path / model_file).exists() for model_file in model_files
            )
            result["has_model_files"] = has_model_files

            if not has_model_files:
                result["errors"].append("No se encontraron archivos de modelo")

            # Verificar archivos de tokenizer
            tokenizer_files = ["tokenizer.json", "tokenizer_config.json", "vocab.txt"]
            has_tokenizer = any(
                (path / tokenizer_file).exists() for tokenizer_file in tokenizer_files
            )
            result["has_tokenizer"] = has_tokenizer

            if not has_tokenizer:
                result["errors"].append("No se encontraron archivos de tokenizer")

            # Si no hay errores, el modelo es válido
            if not result["errors"]:
                result["valid"] = True

        except Exception as e:
            result["errors"].append(f"Error durante la validación: {str(e)}")

        return result

    def get_model_info(self, model_path: str) -> Dict[str, Any]:
        """
        Obtener información de un modelo

        Args:
            model_path: Ruta del modelo

        Returns:
            Dict: Información del modelo
        """
        info = {
            "path": model_path,
            "size_bytes": 0,
            "size_gb": 0,
            "file_count": 0,
            "files": [],
            "config": None,
            "model_type": "unknown",
        }

        try:
            path = Path(model_path)
            if not path.exists():
                return info

            # Calcular tamaño total
            total_size = 0
            file_count = 0
            files = []

            for file_path in path.rglob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    file_count += 1
                    files.append(
                        {
                            "name": file_path.name,
                            "size_bytes": file_size,
                            "size_mb": file_size / (1024**2),
                            "relative_path": str(file_path.relative_to(path)),
                        }
                    )

            info["size_bytes"] = total_size
            info["size_gb"] = total_size / (1024**3)
            info["file_count"] = file_count
            info["files"] = files

            # Cargar configuración
            config_path = path / "config.json"
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    info["config"] = config
                    info["model_type"] = config.get("model_type", "unknown")
                except Exception as e:
                    self.logger.warning(f"Error cargando configuración: {e}")

        except Exception as e:
            self.logger.error(f"Error obteniendo información del modelo: {e}")

        return info

    def calculate_model_hash(self, model_path: str, algorithm: str = "sha256") -> str:
        """
        Calcular hash de un modelo

        Args:
            model_path: Ruta del modelo
            algorithm: Algoritmo de hash

        Returns:
            str: Hash del modelo
        """
        try:
            path = Path(model_path)
            if not path.exists():
                raise ValueError("La ruta del modelo no existe")

            # Crear hash
            if algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "md5":
                hash_obj = hashlib.md5()
            else:
                raise ValueError(f"Algoritmo de hash no soportado: {algorithm}")

            # Procesar archivos en orden alfabético
            files = sorted(path.rglob("*"))
            for file_path in files:
                if file_path.is_file():
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_obj.update(chunk)

            return hash_obj.hexdigest()

        except Exception as e:
            self.logger.error(f"Error calculando hash del modelo: {e}")
            return ""

    def copy_model(
        self, source_path: str, dest_path: str, overwrite: bool = False
    ) -> bool:
        """
        Copiar modelo a nueva ubicación

        Args:
            source_path: Ruta origen
            dest_path: Ruta destino
            overwrite: Sobrescribir si existe

        Returns:
            bool: True si se copió exitosamente
        """
        try:
            source = Path(source_path)
            dest = Path(dest_path)

            if not source.exists():
                raise ValueError(f"Ruta origen no existe: {source_path}")

            if dest.exists() and not overwrite:
                raise ValueError(f"Ruta destino ya existe: {dest_path}")

            # Crear directorio destino
            dest.mkdir(parents=True, exist_ok=True)

            # Copiar archivos
            shutil.copytree(source, dest, dirs_exist_ok=overwrite)

            self.logger.info(f"Modelo copiado de {source_path} a {dest_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error copiando modelo: {e}")
            return False

    def backup_model(self, model_path: str, backup_dir: str) -> str:
        """
        Crear backup de un modelo

        Args:
            model_path: Ruta del modelo
            backup_dir: Directorio de backup

        Returns:
            str: Ruta del backup creado
        """
        try:
            import datetime

            model_name = Path(model_path).name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{model_name}_backup_{timestamp}"
            backup_path = Path(backup_dir) / backup_name

            if self.copy_model(model_path, str(backup_path)):
                self.logger.info(f"Backup creado: {backup_path}")
                return str(backup_path)
            else:
                raise Exception("Error durante la copia")

        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return ""

    def cleanup_model_files(
        self, model_path: str, keep_extensions: Optional[List[str]] = None
    ) -> bool:
        """
        Limpiar archivos innecesarios del modelo

        Args:
            model_path: Ruta del modelo
            keep_extensions: Extensiones a mantener

        Returns:
            bool: True si se limpió exitosamente
        """
        if keep_extensions is None:
            keep_extensions = [".json", ".bin", ".safetensors", ".txt", ".model"]

        try:
            path = Path(model_path)
            if not path.exists():
                return False

            removed_count = 0
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    extension = file_path.suffix.lower()
                    if extension not in keep_extensions:
                        file_path.unlink()
                        removed_count += 1

            self.logger.info(f"Archivos limpiados: {removed_count}")
            return True

        except Exception as e:
            self.logger.error(f"Error limpiando archivos: {e}")
            return False

    def compress_model(self, model_path: str, output_path: str) -> bool:
        """
        Comprimir modelo en archivo tar.gz

        Args:
            model_path: Ruta del modelo
            output_path: Ruta del archivo comprimido

        Returns:
            bool: True si se comprimió exitosamente
        """
        try:
            import tarfile

            model_name = Path(model_path).name
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(model_path, arcname=model_name)

            self.logger.info(f"Modelo comprimido: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error comprimiendo modelo: {e}")
            return False

    def extract_model(self, archive_path: str, extract_dir: str) -> str:
        """
        Extraer modelo desde archivo comprimido

        Args:
            archive_path: Ruta del archivo comprimido
            extract_dir: Directorio de extracción

        Returns:
            str: Ruta del modelo extraído
        """
        try:
            import tarfile

            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(extract_dir)

            # Obtener nombre del modelo extraído
            extracted_path = Path(extract_dir)
            model_dirs = [d for d in extracted_path.iterdir() if d.is_dir()]

            if model_dirs:
                model_path = str(model_dirs[0])
                self.logger.info(f"Modelo extraído: {model_path}")
                return model_path
            else:
                raise Exception("No se encontró directorio de modelo en el archivo")

        except Exception as e:
            self.logger.error(f"Error extrayendo modelo: {e}")
            return ""

    def get_model_dependencies(self, model_path: str) -> Dict[str, Any]:
        """
        Obtener dependencias de un modelo

        Args:
            model_path: Ruta del modelo

        Returns:
            Dict: Dependencias del modelo
        """
        dependencies = {
            "transformers": ">=4.0.0",
            "torch": ">=1.9.0",
            "tokenizers": ">=0.10.0",
            "accelerate": ">=0.20.0",
        }

        try:
            config_path = Path(model_path) / "config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)

                # Determinar dependencias específicas basadas en el tipo de modelo
                model_type = config.get("model_type", "")

                if "llama" in model_type.lower():
                    dependencies["transformers"] = ">=4.30.0"
                elif "gpt" in model_type.lower():
                    dependencies["transformers"] = ">=4.20.0"
                elif "bert" in model_type.lower():
                    dependencies["transformers"] = ">=4.15.0"

                # Verificar si usa cuantización
                if config.get("quantization_config"):
                    dependencies["accelerate"] = ">=0.20.0"

        except Exception as e:
            self.logger.warning(f"Error obteniendo dependencias: {e}")

        return dependencies

    def validate_model_compatibility(
        self, model_path: str, device: str = "auto"
    ) -> Dict[str, Any]:
        """
        Validar compatibilidad del modelo con el sistema

        Args:
            model_path: Ruta del modelo
            device: Dispositivo objetivo

        Returns:
            Dict: Resultado de la validación de compatibilidad
        """
        result = {
            "compatible": False,
            "device_supported": False,
            "memory_sufficient": False,
            "dependencies_met": False,
            "warnings": [],
            "errors": [],
        }

        try:
            # Obtener información del modelo
            model_info = self.get_model_info(model_path)
            model_size_gb = model_info["size_gb"]

            # Verificar dispositivo
            target_device = self.device_utils.get_optimal_device(device)
            device_info = self.device_utils.get_device_info(target_device)

            if device_info and device_info.is_available:
                result["device_supported"] = True
            else:
                result["errors"].append(f"Dispositivo {target_device} no disponible")

            # Verificar memoria
            memory_check = self.memory_manager.can_load_model(
                model_size_gb, target_device
            )
            if memory_check["can_load"]:
                result["memory_sufficient"] = True
            else:
                result["warnings"].append(
                    f"Memoria insuficiente: {memory_check['margin_gb']:.2f}GB disponible"
                )

            # Verificar dependencias (simplificado)
            try:
                import transformers
                import torch

                result["dependencies_met"] = True
            except ImportError as e:
                result["errors"].append(f"Dependencia faltante: {e}")

            # Determinar compatibilidad general
            if (
                result["device_supported"]
                and result["memory_sufficient"]
                and result["dependencies_met"]
            ):
                result["compatible"] = True

        except Exception as e:
            result["errors"].append(f"Error durante validación: {str(e)}")

        return result

    def get_model_metadata(self, model_path: str) -> Dict[str, Any]:
        """
        Obtener metadatos de un modelo

        Args:
            model_path: Ruta del modelo

        Returns:
            Dict: Metadatos del modelo
        """
        metadata = {
            "name": "",
            "version": "",
            "description": "",
            "author": "",
            "license": "",
            "tags": [],
            "created_date": "",
            "modified_date": "",
            "model_type": "",
            "parameters": 0,
            "vocab_size": 0,
        }

        try:
            path = Path(model_path)

            # Cargar configuración
            config_path = path / "config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)

                metadata.update(
                    {
                        "model_type": config.get("model_type", ""),
                        "parameters": config.get("num_parameters", 0),
                        "vocab_size": config.get("vocab_size", 0),
                    }
                )

            # Cargar metadatos específicos
            metadata_path = path / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    model_metadata = json.load(f)
                metadata.update(model_metadata)

            # Obtener fechas de archivos
            if path.exists():
                stat = path.stat()
                metadata["created_date"] = str(stat.st_ctime)
                metadata["modified_date"] = str(stat.st_mtime)

        except Exception as e:
            self.logger.warning(f"Error obteniendo metadatos: {e}")

        return metadata
