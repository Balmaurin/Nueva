import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import torch
from transformers import AutoModel, AutoTokenizer
from peft import PeftModel, get_peft_model, LoraConfig


class BranchManager:
    """
    Gestor completo de ramas para Shaili-AI
    Maneja las 32 macro-ramas y sus micro-ramas especializadas
    """

    def __init__(self, base_model_path: str = "models/custom/shaili-personal-model"):
        """
        Inicializar gestor de ramas

        Args:
            base_model_path (str): Ruta al modelo base
        """
        self.logger = logging.getLogger(__name__)
        self.base_model_path = base_model_path

        # Cargar configuración de ramas
        self.branches_config = self._load_branches_config()

        # Mapeo de dominios a ramas
        self.domain_to_branch = {
            "Lengua y Lingüística": "lengua_y_lingüística",
            "Matemáticas": "matemáticas",
            "Computación y Programación": "computación_y_programación",
            "Ciencia de Datos e IA": "ciencia_de_datos_e_ia",
            "Física": "física",
            "Química": "química",
            "Biología": "biología",
            "Medicina y Salud": "medicina_y_salud",
            "Neurociencia y Psicología": "neurociencia_y_psicología",
            "Ingeniería": "ingeniería",
            "Electrónica y IoT": "electrónica_y_iot",
            "Ciberseguridad y Criptografía": "ciberseguridad_y_criptografía",
            "Sistemas, DevOps y Redes": "sistemas_devops_redes",
            "Ciencias de la Tierra y Clima": "ciencias_de_la_tierra_y_clima",
            "Astronomía y Espacio": "astronomía_y_espacio",
            "Economía y Finanzas": "economía_y_finanzas",
            "Empresa y Emprendimiento": "empresa_y_emprendimiento",
            "Derecho y Políticas Públicas": "derecho_y_políticas_públicas",
            "Sociología y Antropología": "sociología_y_antropología",
            "Educación y Pedagogía": "educación_y_pedagogía",
            "Historia": "historia",
            "Geografía y Geo-Política": "geografía_y_geo_política",
            "Arte, Música y Cultura": "arte_música_y_cultura",
            "Literatura y Escritura": "literatura_y_escritura",
            "Medios y Comunicación": "medios_y_comunicación",
            "Diseño y UX": "diseño_y_ux",
            "Deportes y eSports": "deportes_y_esports",
            "Juegos y Entretenimiento": "juegos_y_entretenimiento",
            "Hogar, DIY y Reparaciones": "hogar_diy_y_reparaciones",
            "Cocina y Nutrición": "cocina_y_nutrición",
            "Viajes e Idiomas": "viajes_e_idiomas",
            "Vida Diaria, Legal, Práctico y Trámites": "vida_diaria_legal_práctico_y_trámites",
        }

        # Micro-ramas por dominio
        self.micro_branches = self._load_micro_branches()

        # Caché de adapters cargados
        self.loaded_adapters = {}

        self.logger.info(
            f"✅ BranchManager inicializado con {len(self.domain_to_branch)} dominios"
        )

    def _load_branches_config(self) -> Dict[str, Any]:
        """Cargar configuración de ramas desde JSON"""
        config_path = "models/branches/base_branches.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(
                f"Configuración de ramas no encontrada en {config_path}"
            )
            return {"domains": []}

    def _load_micro_branches(self) -> Dict[str, List[str]]:
        """Cargar micro-ramas desde los directorios de cada rama"""
        micro_branches = {}

        for domain, branch_path in self.domain_to_branch.items():
            full_path = f"models/branches/{branch_path}/microramas"
            if os.path.exists(full_path):
                try:
                    with open(
                        f"{full_path}/microramas.json", "r", encoding="utf-8"
                    ) as f:
                        data = json.load(f)
                        micro_branches[domain] = data.get("microramas", [])
                except FileNotFoundError:
                    micro_branches[domain] = []
            else:
                micro_branches[domain] = []

        return micro_branches

    def get_available_domains(self) -> List[str]:
        """Obtener lista de dominios disponibles"""
        return list(self.domain_to_branch.keys())

    def get_micro_branches(self, domain: str) -> List[str]:
        """Obtener micro-ramas de un dominio específico"""
        return self.micro_branches.get(domain, [])

    def load_adapter(self, domain: str, adapter_path: str = None) -> Optional[Any]:
        """
        Cargar adapter para una rama específica

        Args:
            domain (str): Dominio de la rama
            adapter_path (str, opcional): Ruta específica del adapter

        Returns:
            Modelo con adapter cargado o None si falla
        """
        try:
            # Determinar ruta del adapter
            if adapter_path is None:
                branch_name = self.domain_to_branch.get(domain)
                if not branch_name:
                    self.logger.error(f"Dominio no encontrado: {domain}")
                    return None

                adapter_path = f"models/branches/{branch_name}/adapter"

            # Verificar si el adapter existe
            if not os.path.exists(adapter_path):
                self.logger.warning(f"Adapter no encontrado en: {adapter_path}")
                return None

            # Cargar modelo base
            tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
            base_model = AutoModel.from_pretrained(self.base_model_path)

            # Cargar adapter
            adapter_model = PeftModel.from_pretrained(base_model, adapter_path)

            # Configurar para inferencia
            adapter_model.eval()

            self.logger.info(f"✅ Adapter cargado para dominio: {domain}")
            return adapter_model

        except Exception as e:
            self.logger.error(f"Error cargando adapter para {domain}: {e}")
            return None

    def create_adapter(self, domain: str, training_data: List[Dict[str, str]]) -> bool:
        """
        Crear nuevo adapter para una rama

        Args:
            domain (str): Dominio de la rama
            training_data (list): Datos de entrenamiento

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            branch_name = self.domain_to_branch.get(domain)
            if not branch_name:
                self.logger.error(f"Dominio no válido: {domain}")
                return False

            # Configurar LoRA
            lora_config = LoraConfig(
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "v_proj"],
                lora_dropout=0.05,
                bias="none",
                task_type="CAUSAL_LM",
            )

            # Cargar modelo base
            base_model = AutoModel.from_pretrained(self.base_model_path)

            # Crear modelo con LoRA
            peft_model = get_peft_model(base_model, lora_config)

            # Entrenar adapter (simplificado)
            # En implementación real, aquí iría el entrenamiento completo

            # Guardar adapter
            adapter_path = f"models/branches/{branch_name}/adapter"
            os.makedirs(adapter_path, exist_ok=True)
            peft_model.save_pretrained(adapter_path)

            self.logger.info(f"✅ Adapter creado para dominio: {domain}")
            return True

        except Exception as e:
            self.logger.error(f"Error creando adapter para {domain}: {e}")
            return False

    def detect_emerging_branch(self, interactions: Dict[str, Any]) -> Optional[str]:
        """
        Detectar ramas emergentes basado en interacciones

        Args:
            interactions (dict): Interacciones del usuario

        Returns:
            str: Nombre de la rama emergente o None
        """
        try:
            # Análisis de patrones en interacciones
            query_patterns = interactions.get("queries", [])

            # Detectar dominios frecuentes
            domain_counts = {}
            for query in query_patterns:
                # Clasificación simple por palabras clave
                for domain in self.domain_to_branch.keys():
                    if any(
                        keyword in query.lower() for keyword in domain.lower().split()
                    ):
                        domain_counts[domain] = domain_counts.get(domain, 0) + 1

            # Identificar dominio más frecuente
            if domain_counts:
                most_frequent = max(domain_counts, key=domain_counts.get)
                if domain_counts[most_frequent] >= 3:  # Umbral mínimo
                    return most_frequent

            return None

        except Exception as e:
            self.logger.error(f"Error detectando rama emergente: {e}")
            return None

    def get_branch_status(self, domain: str) -> Dict[str, Any]:
        """
        Obtener estado de una rama específica

        Args:
            domain (str): Dominio de la rama

        Returns:
            dict: Estado de la rama
        """
        try:
            branch_name = self.domain_to_branch.get(domain)
            if not branch_name:
                return {"error": "Dominio no encontrado"}

            branch_path = f"models/branches/{branch_name}"

            status = {
                "domain": domain,
                "branch_name": branch_name,
                "adapter_exists": os.path.exists(f"{branch_path}/adapter"),
                "micro_branches": self.get_micro_branches(domain),
                "last_updated": datetime.now().isoformat(),
            }

            return status

        except Exception as e:
            self.logger.error(f"Error obteniendo estado de rama {domain}: {e}")
            return {"error": str(e)}

    def get_all_branches_status(self) -> Dict[str, Any]:
        """Obtener estado de todas las ramas"""
        status = {}
        for domain in self.domain_to_branch.keys():
            status[domain] = self.get_branch_status(domain)
        return status


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
