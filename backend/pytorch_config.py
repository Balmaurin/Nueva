#!/usr/bin/env python3
"""
Configuración de PyTorch para minimizar warnings y errores
"""

import os
import warnings
import torch


def configure_pytorch():
    """Configurar PyTorch para minimizar warnings"""

    # Configurar variables de entorno
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Configurar warnings de Python
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # Configurar warnings específicos de PyTorch
    if hasattr(torch, "set_warn_always"):
        torch.set_warn_always(False)

    # Configurar para evitar warnings de flash-attention
    os.environ["FLASH_ATTENTION_DISABLE"] = "1"

    # Configurar logging de transformers
    try:
        import transformers

        transformers.logging.set_verbosity_error()
    except ImportError:
        pass

    # Configurar para evitar warnings de accelerate
    try:
        import accelerate

        os.environ["ACCELERATE_LOG_LEVEL"] = "error"
    except ImportError:
        pass


def get_device_info():
    """Obtener información del dispositivo"""
    info = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "current_device": (
            torch.cuda.current_device() if torch.cuda.is_available() else None
        ),
        "device_name": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        ),
        "memory_total": None,
        "memory_free": None,
    }

    if torch.cuda.is_available():
        try:
            props = torch.cuda.get_device_properties(0)
            info["memory_total"] = props.total_memory / 1024**3  # GB
            info["memory_free"] = torch.cuda.memory_reserved(0) / 1024**3  # GB
        except Exception:
            pass

    return info


def optimize_memory():
    """Optimizar uso de memoria"""
    if torch.cuda.is_available():
        # Limpiar caché de CUDA
        torch.cuda.empty_cache()

        # Configurar para usar memoria de manera eficiente
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False

        # Configurar para evitar fragmentación de memoria
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "max_split_size_mb:128,expandable_segments:False"
        )
