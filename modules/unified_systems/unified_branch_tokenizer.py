#!/usr/bin/env python3
"""
Tokenizador Unificado de Ramas para NeuroFusion
===============================================
Sistema de tokenización que maneja múltiples ramas de especialización
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re

logger = logging.getLogger(__name__)


class VocabBuilder20Branches:
    """Constructor de vocabulario para 20 ramas de especialización"""

    def __init__(self):
        self.branch_vocabs = {}
        self.unified_vocab = {}
        self.special_tokens = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3,
            "<SEP>": 4,
            "<MASK>": 5,
        }

        # Inicializar vocabularios de ramas
        self._initialize_branch_vocabs()

    def _initialize_branch_vocabs(self):
        """Inicializar vocabularios para cada rama"""
        branches = [
            "tech",
            "science",
            "health",
            "finance",
            "education",
            "entertainment",
            "sports",
            "politics",
            "environment",
            "culture",
            "business",
            "travel",
            "food",
            "fashion",
            "art",
            "music",
            "literature",
            "history",
            "philosophy",
            "religion",
        ]

        for branch in branches:
            self.branch_vocabs[branch] = Counter()

    def update_branch_vocab(self, branch: str, text: str):
        """Actualizar vocabulario de una rama específica"""
        if branch not in self.branch_vocabs:
            self.branch_vocabs[branch] = Counter()

        # Tokenizar texto
        tokens = self._tokenize_text(text)

        # Agregar prefijo de rama
        branch_tokens = [f"{branch}::{token}" for token in tokens]

        # Actualizar contador
        self.branch_vocabs[branch].update(branch_tokens)

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenización básica del texto"""
        # Limpiar texto
        text = re.sub(r"[^\w\s]", " ", text.lower())

        # Dividir en tokens
        tokens = text.split()

        return tokens

    def get_unified_vocab(self) -> Dict[str, int]:
        """Obtener vocabulario unificado"""
        vocab = {}
        token_id = 0

        # Agregar tokens especiales
        for token, _ in self.special_tokens.items():
            vocab[token] = token_id
            token_id += 1

        # Agregar tokens de todas las ramas
        for branch, branch_vocab in self.branch_vocabs.items():
            for token, count in branch_vocab.most_common(1000):  # Top 1000 por rama
                if token not in vocab:
                    vocab[token] = token_id
                    token_id += 1

        return vocab


class UnifiedBranchTokenizer:
    """Tokenizador unificado para múltiples ramas de especialización"""

    def __init__(self, vocab_builder: Optional[VocabBuilder20Branches] = None):
        self.vocab_builder = vocab_builder or VocabBuilder20Branches()
        self.unified_vocab = self.vocab_builder.get_unified_vocab()
        self.id2token = {idx: token for token, idx in self.unified_vocab.items()}
        self.vocab_size = len(self.unified_vocab)

        # Mapeo de prefijos a ramas
        self.prefix_to_branch = {
            "tech": "tech",
            "science": "science",
            "health": "health",
            "finance": "finance",
            "education": "education",
            "entertainment": "entertainment",
            "sports": "sports",
            "politics": "politics",
            "environment": "environment",
            "culture": "culture",
            "business": "business",
            "travel": "travel",
            "food": "food",
            "fashion": "fashion",
            "art": "art",
            "music": "music",
            "literature": "literature",
            "history": "history",
            "philosophy": "philosophy",
            "religion": "religion",
        }

        # Tokens especiales
        self.special_tokens = self.vocab_builder.special_tokens

        logger.info(
            f"✅ Tokenizador unificado inicializado con {self.vocab_size} tokens"
        )

    def tokenize(self, text: str, branch: Optional[str] = None) -> List[int]:
        """Tokenizar texto"""
        # Tokenización básica
        tokens = self.vocab_builder._tokenize_text(text)

        # Convertir a IDs
        token_ids = []
        for token in tokens:
            if branch and branch in self.prefix_to_branch:
                # Agregar prefijo de rama
                branch_token = f"{branch}::{token}"
                if branch_token in self.unified_vocab:
                    token_ids.append(self.unified_vocab[branch_token])
                else:
                    token_ids.append(
                        self.unified_vocab.get(token, self.unified_vocab["<UNK>"])
                    )
            else:
                # Token sin rama específica
                token_ids.append(
                    self.unified_vocab.get(token, self.unified_vocab["<UNK>"])
                )

        return token_ids

    def detokenize(self, token_ids: List[int]) -> str:
        """Convertir IDs de tokens de vuelta a texto"""
        tokens = []
        for token_id in token_ids:
            if token_id in self.id2token:
                token = self.id2token[token_id]
                # Remover prefijo de rama si existe
                if "::" in token:
                    token = token.split("::", 1)[1]
                tokens.append(token)
            else:
                tokens.append("<UNK>")

        return " ".join(tokens)

    def detect_active_branches(self, text: str) -> List[str]:
        """Detectar qué ramas están activas en el texto"""
        active_branches = set()

        for branch in self.prefix_to_branch.keys():
            if branch in text.lower():
                active_branches.add(branch)

        return list(active_branches)

    def suggest_branches(self, text: str) -> List[Tuple[str, float]]:
        """Sugerir ramas basándose en el contenido del texto"""
        # Análisis simple basado en palabras clave
        branch_keywords = {
            "tech": ["technology", "software", "computer", "programming", "code"],
            "science": ["science", "research", "experiment", "discovery", "theory"],
            "health": ["health", "medical", "doctor", "patient", "treatment"],
            "finance": ["money", "finance", "bank", "investment", "economy"],
            "education": ["education", "learning", "school", "student", "teacher"],
        }

        text_lower = text.lower()
        branch_scores = Counter()

        for branch, keywords in branch_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    branch_scores[branch] += 1

        total_words = len(text.split())
        if total_words == 0:
            return []

        suggestions = []
        for branch, count in branch_scores.most_common():
            score = count / total_words
            suggestions.append((branch, score))

        return suggestions

    def get_vocab_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del vocabulario"""
        stats = {
            "total_vocab_size": len(self.unified_vocab),
            "special_tokens_size": len(self.special_tokens),
            "branches": {},
        }

        for branch in self.prefix_to_branch.keys():
            if branch == "global":
                continue

            branch_tokens = [
                token
                for token in self.unified_vocab.keys()
                if token.startswith(f"{branch}::")
            ]

            stats["branches"][branch] = {
                "vocab_size": len(branch_tokens),
                "tokens": branch_tokens[:10],  # Primeros 10 tokens
            }

        return stats

    def update_from_text(self, text: str, branch: str):
        """Actualizar vocabulario de una rama con nuevo texto"""
        self.vocab_builder.update_branch_vocab(branch, text)

        # Reconstruir vocabulario unificado
        self.unified_vocab = self.vocab_builder.get_unified_vocab()
        self.id2token = {idx: token for token, idx in self.unified_vocab.items()}

        # Actualizar vocab_size
        self.vocab_size = len(self.unified_vocab)

        logger.info(f"🔄 Tokenizador actualizado con texto de rama {branch}")

    def save(self, path: str):
        """Guardar el tokenizador"""
        import json

        config = {
            "unified_vocab": self.unified_vocab,
            "special_tokens": self.special_tokens,
            "prefix_to_branch": self.prefix_to_branch,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Tokenizador unificado guardado en {path}")

    @classmethod
    def load(cls, path: str, vocab_builder: Optional[VocabBuilder20Branches] = None):
        """Cargar el tokenizador"""
        import json

        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        tokenizer = cls(vocab_builder)
        tokenizer.unified_vocab = config["unified_vocab"]
        tokenizer.id2token = {
            idx: token for token, idx in tokenizer.unified_vocab.items()
        }
        tokenizer.special_tokens = config["special_tokens"]
        tokenizer.prefix_to_branch = config["prefix_to_branch"]
        tokenizer.vocab_size = len(tokenizer.unified_vocab)

        logger.info(f"📂 Tokenizador unificado cargado desde {path}")
        return tokenizer

    def get_branch_tokens(self, branch: str) -> List[str]:
        """Obtener todos los tokens de una rama específica"""
        if branch not in self.prefix_to_branch:
            return []

        return [
            token
            for token in self.unified_vocab.keys()
            if token.startswith(f"{branch}::")
        ]

    def get_specialization_tokens(self, branch: str, specialization: str) -> List[str]:
        """Obtener tokens de una especialización específica"""
        branch_tokens = self.get_branch_tokens(branch)
        specialization_tokens = []

        for token in branch_tokens:
            if specialization.lower() in token.lower():
                specialization_tokens.append(token)

        return specialization_tokens
