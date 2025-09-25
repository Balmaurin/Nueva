from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from ai.llm_core.real_transformer import NeuroFusionTransformer, TransformerConfig
from ai.llm_core.weights_initializer import initialize_neurofusion_weights
from core.tensors.gradient_optimizer import GradientOptimizer

logger = logging.getLogger(__name__)


class ToyTextDataset(Dataset):
    def __init__(self, sequences: List[List[int]], seq_len: int):
        self.data = [seq[:seq_len] for seq in sequences]
        self.seq_len = seq_len

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int):
        return x, y


@dataclass
class TrainConfig:
    batch_size: int = 8
    lr: float = 3e-4
    epochs: int = 1
    seq_len: int = 64
    device: str = "cpu"
    early_stop_patience: int = 3
    use_advanced_optimizer: bool = True
    use_mixed_precision: bool = False


def train_minimal_pipeline() -> NeuroFusionTransformer:
    model = NeuroFusionTransformer(TransformerConfig())
    initialize_neurofusion_weights(model)
    model.train()

    # Usar optimizador avanzado personalizado
    if cfg.use_advanced_optimizer:
        logger.info("🚀 Usando optimizador de gradientes avanzado")
        optimizer = GradientOptimizer()

        # Activar optimizador
        if not optimizer.activate():
            logger.error(
                "❌ Error activando optimizador avanzado, usando AdamW estándar"
            )
            optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
        else:
            # Registrar parámetros del modelo
            optimizer.register_parameters(list(model.parameters()))
            logger.info(
                f"✅ Optimizador avanzado activado con {len(list(model.parameters()))} parámetros"
            )
    else:
        logger.info("📊 Usando optimizador AdamW estándar")
        optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr)

    # Dataset juguete determinista

    patience = 0

    for epoch in range(cfg.epochs):
        total_loss = 0.0
        for batch_idx, (x, y) in enumerate(dl):
            loss = criterion(logits.reshape(-1, logits.size(-1)), y.reshape(-1))

            # Usar optimizador avanzado o estándar
            if cfg.use_advanced_optimizer and isinstance(optimizer, GradientOptimizer):
                # Limpiar gradientes
                optimizer.zero_grad()

                # Backward pass
                loss.backward()

                # Optimizar con nuestro optimizador personalizado

                # Mostrar estadísticas cada 10 batches
                if batch_idx % 10 == 0:
                    logger.info(
                        f"Batch {batch_idx} - Optimizaciones: {stats['optimizations']}, "
                        f"Gradientes recortados: {stats['clipped_gradients']}"
                    )
            else:
                # Optimizador estándar
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            total_loss += loss.item()

        logger.info(f"Epoch {epoch+1} - loss: {avg_loss:.4f}")

        # Mostrar estadísticas del optimizador avanzado al final de cada época
        if cfg.use_advanced_optimizer and isinstance(optimizer, GradientOptimizer):
            logger.info(
                f"📊 Estadísticas época {epoch+1}: "
                f"Optimizaciones: {stats['optimizations']}, "
                f"Tiempo promedio: {stats['avg_optimization_time']:.2f}ms, "
                f"Norma gradientes: {stats.get('avg_gradient_norm', 0):.4f}"
            )

        if avg_loss < best_loss - 1e-4:
            patience = 0
        else:
            patience += 1
            if patience >= cfg.early_stop_patience:
                logger.info("Early stopping")
                break

    # Mostrar estadísticas finales del optimizador
    if cfg.use_advanced_optimizer and isinstance(optimizer, GradientOptimizer):
        logger.info("🎯 Estadísticas finales del optimizador avanzado:")
        for key, value in final_stats.items():
            if isinstance(value, dict):
                logger.info(f"  {key}:")
                for k, v in value.items():
                    logger.info(f"    {k}: {v}")
            else:
                logger.info(f"  {key}: {value}")

    return model
