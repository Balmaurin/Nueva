import json
import os
from typing import List, Dict
import numpy as np

# sentence_transformers removido


class ShortTermMemory:
    def __init__(
        self, max_messages: int = 10, max_tokens: int = 1024, summary_every: int = 8000
    ):
        """
        Inicializar memoria de corto plazo

        Args:
            max_messages: Número máximo de mensajes a mantener
            max_tokens: Límite máximo de tokens
            summary_every: Resumir cada N tokens
        """
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.summary_every = summary_every

        # Modelo de embeddings para similitud semántica
        # Usar el modelo principal para embeddings
        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(
            "models/custom/shaili-personal-model"
        )
        self.embedding_model = AutoModel.from_pretrained(
            "models/custom/shaili-personal-model"
        )

        # Directorio de almacenamiento
        self.memory_dir = "memory/short_term"
        os.makedirs(self.memory_dir, exist_ok=True)

        # Estado de la memoria
        self.messages = []
        self.current_tokens = 0

    def add_message(
        self, role: str, content: str, tokens: int = None, metadata: Dict = None
    ):
        """
        Añadir mensaje a la memoria de corto plazo

        Args:
            role: Rol del mensaje (user, assistant, system)
            content: Contenido del mensaje
            tokens: Número de tokens (opcional)
            metadata: Metadatos adicionales
        """
        # Calcular tokens si no se proporcionan
        if tokens is None:
            tokens = len(self.embedding_model.tokenizer.encode(content))

        # Generar embedding
        embedding = self.embedding_model.encode(content)

        # Preparar mensaje
        message = {
            "role": role,
            "content": content,
            "tokens": tokens,
            "embedding": embedding.tolist(),
            "metadata": metadata or {},
        }

        # Gestionar límite de tokens
        if self.current_tokens + tokens > self.max_tokens:
            self._prune_messages(tokens)

        # Añadir mensaje
        self.messages.append(message)
        self.current_tokens += tokens

        # Resumir si es necesario
        if self.current_tokens >= self.summary_every:
            self._summarize()

    def _prune_messages(self, new_tokens: int):
        """
        Eliminar mensajes antiguos para hacer espacio

        Args:
            new_tokens: Número de tokens del nuevo mensaje
        """
        while self.current_tokens + new_tokens > self.max_tokens and self.messages:
            removed_message = self.messages.pop(0)
            self.current_tokens -= removed_message["tokens"]

    def _summarize(self):
        """
        Resumir conversación para reducir tokens
        """
        # Implementar resumen semántico
        # Usar técnicas como:
        # 1. Clustering de embeddings
        # 2. Selección de mensajes más representativos
        # 3. Generación de resumen abstractivo
        pass

    def get_context(
        self, max_tokens: int = None, include_system: bool = True
    ) -> List[Dict]:
        """
        Obtener contexto actual

        Args:
            max_tokens: Límite de tokens a devolver
            include_system: Incluir mensajes de sistema

        Returns:
            Lista de mensajes de contexto
        """
        max_tokens = max_tokens or self.max_tokens
        context = []
        current_tokens = 0

        # Iterar desde el final
        for message in reversed(self.messages):
            if not include_system and message["role"] == "system":
                continue

            if current_tokens + message["tokens"] > max_tokens:
                break

            context.insert(0, message)
            current_tokens += message["tokens"]

        return context

    def save(self, session_id: str = None):
        """
        Guardar estado de la memoria

        Args:
            session_id: Identificador de sesión
        """
        session_id = session_id or "default"
        filename = os.path.join(self.memory_dir, f"{session_id}_memory.json")

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {"messages": self.messages, "current_tokens": self.current_tokens},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def load(self, session_id: str = None):
        """
        Cargar estado de la memoria

        Args:
            session_id: Identificador de sesión
        """
        session_id = session_id or "default"
        filename = os.path.join(self.memory_dir, f"{session_id}_memory.json")

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.messages = data["messages"]
                self.current_tokens = data["current_tokens"]

    def clear(self):
        """Limpiar memoria"""
        self.messages = []
        self.current_tokens = 0


def main():
    # Ejemplo de uso
    memory = ShortTermMemory()

    # Añadir mensajes
    memory.add_message("user", "Hola, ¿qué es la fotosíntesis?")
    memory.add_message("assistant", "La fotosíntesis es un proceso...")

    # Obtener contexto
    context = memory.get_context()
    for msg in context:
        print(f"{msg['role']}: {msg['content']}")

    # Guardar memoria
    memory.save("sesion_ejemplo")


if __name__ == "__main__":
    main()
