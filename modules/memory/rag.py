import os
import json
import logging
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
import torch
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import LargeBinary, JSON

Base = declarative_base()


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    source = sa.Column(sa.Text)
    content = sa.Column(sa.Text)
    domain = sa.Column(sa.Text)
    embedding = sa.Column(LargeBinary)
    metadata = sa.Column(JSON)


class RAGRetriever:
    def __init__(
        self,
        embed_model: str = "models/custom/shaili-personal-model",
        db_url: str = "postgresql://user:password@localhost/sheily_db",
        index_path: str = "data/faiss_index.index",
    ):
        """
        Sistema de Recuperación Aumentada con Generación (RAG) con citación

        Args:
            embed_model (str): Modelo de embeddings
            db_url (str): URL de conexión a PostgreSQL
            index_path (str): Ruta del índice FAISS
        """
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Cargar modelo de embeddings
        # Usar el modelo principal para embeddings
        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(embed_model)
        self.embed_model = AutoModel.from_pretrained(embed_model)

        # Conexión a base de datos
        self.engine = sa.create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Cargar o crear índice FAISS
        self.index_path = index_path
        self.index = self._load_or_create_index()

    def _load_or_create_index(self) -> faiss.Index:
        """
        Cargar o crear índice FAISS

        Returns:
            Índice FAISS para búsqueda semántica
        """
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)

        # Crear índice nuevo
        dimension = self.embed_model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatL2(dimension)
        faiss.write_index(index, self.index_path)

        return index

    def add_document(
        self, content: str, source: str, domain: str, metadata: Optional[Dict] = None
    ):
        """
        Añadir documento al sistema RAG

        Args:
            content (str): Contenido del documento
            source (str): Fuente del documento
            domain (str): Dominio del documento
            metadata (dict, opcional): Metadatos adicionales
        """
        # Generar embedding
        # Generar embeddings usando el modelo principal
        inputs = self.tokenizer(
            content, return_tensors="pt", padding=True, truncation=True
        )
        with torch.no_grad():
            outputs = self.embed_model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()

        # Insertar en base de datos
        session = self.Session()
        try:
            rag_doc = RAGDocument(
                source=source,
                content=content,
                domain=domain,
                embedding=embedding.tobytes(),
                metadata=metadata or {},
            )
            session.add(rag_doc)
            session.commit()

            # Añadir al índice FAISS
            self.index.add(np.array([embedding]))
            faiss.write_index(self.index, self.index_path)

            self.logger.info(f"Documento añadido: {source}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error añadiendo documento: {e}")
        finally:
            session.close()

    def _get_query_embedding(self, query: str) -> np.ndarray:
        """
        Generar embedding de consulta

        Args:
            query (str): Consulta de búsqueda

        Returns:
            Embedding de la consulta
        """
        inputs = self.tokenizer(
            query, return_tensors="pt", padding=True, truncation=True
        )
        with torch.no_grad():
            outputs = self.embed_model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).cpu().numpy()

    def _get_document_by_id(
        self, session, idx: int, domain: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Recuperar documento por ID

        Args:
            session: Sesión de base de datos
            idx (int): ID del documento
            domain (str, opcional): Dominio específico

        Returns:
            Documento recuperado o None
        """
        query = session.query(RAGDocument).filter(RAGDocument.id == idx)
        if domain:
            query = query.filter(RAGDocument.domain == domain)

        doc = query.first()

        return (
            {
                "source": doc.source,
                "content": doc.content,
                "domain": doc.domain,
                "metadata": doc.metadata or {},
            }
            if doc
            else None
        )

    def _calculate_similarity_score(self, distance: float) -> float:
        """
        Convertir distancia a puntuación de similitud

        Args:
            distance (float): Distancia calculada

        Returns:
            Puntuación de similitud
        """
        return 1 / (1 + distance)

    def _build_retrieved_doc(self, doc: Dict, dist: float) -> Dict:
        """
        Construir documento recuperado con información de citación

        Args:
            doc (dict): Documento base
            dist (float): Distancia de similitud

        Returns:
            Documento con información de citación
        """
        similarity_score = self._calculate_similarity_score(dist)
        return {
            **doc,
            "similarity_score": similarity_score,
            "citation": {"type": "semantic_retrieval", "confidence": similarity_score},
        }

    def _search_documents(
        self, query_embedding: np.ndarray, k: int = 3, domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar documentos usando embedding de consulta

        Args:
            query_embedding (np.ndarray): Embedding de consulta
            k (int): Número de documentos a recuperar
            domain (str, opcional): Dominio específico

        Returns:
            Lista de documentos recuperados
        """
        # Búsqueda en índice FAISS
        distances, indices = self.index.search(np.array([query_embedding]), k)

        # Recuperar documentos
        session = self.Session()
        try:
            retrieved_docs = []
            for dist, idx in zip(distances[0], indices[0]):
                doc = self._get_document_by_id(session, idx, domain)

                if doc:
                    retrieved_docs.append(self._build_retrieved_doc(doc, dist))

            return retrieved_docs
        except Exception as e:
            self.logger.error(f"Error recuperando documentos: {e}")
            return []
        finally:
            session.close()

    def _generate_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Generar contexto a partir de documentos recuperados

        Args:
            retrieved_docs (list): Lista de documentos recuperados

        Returns:
            Contexto concatenado
        """
        return "\n\n".join(
            [f"[Fuente: {doc['source']}] {doc['content']}" for doc in retrieved_docs]
        )

    def _generate_response(self, context: str, query: str, model, tokenizer) -> str:
        """
        Generar respuesta usando modelo de lenguaje

        Args:
            context (str): Contexto recuperado
            query (str): Consulta del usuario
            model: Modelo de lenguaje
            tokenizer: Tokenizador

        Returns:
            Respuesta generada
        """
        input_text = f"Contexto: {context}\n\nPregunta: {query}\n\nRespuesta:"
        inputs = tokenizer(input_text, return_tensors="pt")

        outputs = model.generate(
            **inputs, max_new_tokens=256, do_sample=True, temperature=0.7
        )

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate_rag_response(
        self, query: str, model, tokenizer, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generar respuesta con recuperación y citación

        Args:
            query (str): Consulta del usuario
            model: Modelo de lenguaje
            tokenizer: Tokenizador
            domain (str, opcional): Dominio específico

        Returns:
            Respuesta con contexto y citaciones
        """
        # Generar embedding de consulta
        query_embedding = self._get_query_embedding(query)

        # Recuperar documentos
        retrieved_docs = self._search_documents(query_embedding, domain=domain)

        # Preparar contexto
        context = self._generate_context(retrieved_docs)

        # Generar respuesta
        response = self._generate_response(context, query, model, tokenizer)

        return {"response": response, "citations": retrieved_docs, "context": context}
