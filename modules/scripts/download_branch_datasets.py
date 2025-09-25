import os
import json
import logging
import yaml
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from branches.branch_manager import BranchManager
from modules.core.training.data_pipeline import DataCurationPipeline


class BranchDatasetDownloader:
    def __init__(
        self,
        branches_config_path: str = "branches/branches_config.json",
        data_sources_path: str = "utils/data_sources.yaml",
        output_dir: str = "datasets/branch_data",
    ):
        """
        Inicializar descargador de datasets para ramas especializadas

        Args:
            branches_config_path (str): Ruta de configuración de ramas
            data_sources_path (str): Ruta de fuentes de datos
            output_dir (str): Directorio de salida para datasets
        """
        # Configuración de logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Cargar configuraciones
        with open(branches_config_path, "r") as f:
            self.branches_config = json.load(f)

        with open(data_sources_path, "r") as f:
            self.data_sources = yaml.safe_load(f)

        # Gestor de ramas
        self.branch_manager = BranchManager(branches_config_path=branches_config_path)

        # Pipeline de curación de datos
        self.data_curator = DataCurationPipeline()

        # Directorio de salida
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _download_file(
        self, url: str, domain: str, max_retries: int = 3
    ) -> Optional[str]:
        """
        Descargar archivo desde una URL

        Args:
            url (str): URL del archivo
            domain (str): Dominio de la rama
            max_retries (int): Número máximo de reintentos

        Returns:
            Ruta del archivo descargado o None
        """
        try:
            # Parsear URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            # Ruta de guardado
            save_path = os.path.join(
                self.output_dir, domain.lower().replace(" ", "_"), filename
            )

            # Crear directorio si no existe
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Descargar archivo
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            return save_path

        except Exception as e:
            self.logger.error(f"Error descargando {url}: {e}")
            return None

    def download_branch_datasets(
        self, priority_domains: Optional[List[str]] = None, max_workers: int = 4
    ) -> Dict[str, List[str]]:
        """
        Descargar datasets para ramas especializadas

        Args:
            priority_domains (list, opcional): Dominios prioritarios
            max_workers (int): Número máximo de descargas concurrentes

        Returns:
            Diccionario de archivos descargados por dominio
        """
        # Obtener ramas definidas
        branches = self.branch_manager.list_branches()

        # Filtrar dominios prioritarios si se especifican
        if priority_domains:
            branches = {
                macro: micro
                for macro, micro in branches.items()
                if macro in priority_domains
            }

        # Resultados de descarga
        download_results = {}

        # Descargar datasets con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Preparar tareas de descarga
            download_tasks = []
            for macro_branch, _ in branches.items():
                # Obtener fuentes de datos para la rama
                sources = self.data_sources.get("domains", {}).get(macro_branch, [])

                for source in sources:
                    url = source.get("url")
                    if url:
                        task = executor.submit(self._download_file, url, macro_branch)
                        download_tasks.append((macro_branch, task))

            # Procesar descargas
            for macro_branch, task in tqdm(download_tasks, desc="Descargando datasets"):
                try:
                    result = task.result()
                    if result:
                        if macro_branch not in download_results:
                            download_results[macro_branch] = []
                        download_results[macro_branch].append(result)
                except Exception as e:
                    self.logger.error(f"Error en descarga para {macro_branch}: {e}")

        return download_results

    def process_downloaded_datasets(self, downloaded_files: Dict[str, List[str]]):
        """
        Procesar datasets descargados

        Args:
            downloaded_files (dict): Archivos descargados por dominio
        """
        for macro_branch, files in downloaded_files.items():
            # Ingerir y procesar documentos
            documents = []
            for file_path in files:
                try:
                    # Curar documentos
                    domain_documents = self.data_curator.ingest_data(
                        [{"url": file_path}], macro_branch
                    )
                    documents.extend(domain_documents)
                except Exception as e:
                    self.logger.error(f"Error procesando {file_path}: {e}")

            # Preparar dataset de entrenamiento
            if documents:
                training_dataset = self.data_curator.prepare_training_dataset(
                    documents, macro_branch
                )

                # Guardar dataset
                save_path = os.path.join(
                    self.output_dir,
                    macro_branch.lower().replace(" ", "_"),
                    "training_dataset",
                )

                training_dataset.save_to_disk(save_path)
                self.logger.info(
                    f"Dataset de entrenamiento guardado para {macro_branch}"
                )


def main():
    """
    Ejecutar descarga y procesamiento de datasets de ramas
    """
    downloader = BranchDatasetDownloader()

    # Descargar datasets para todas las ramas
    downloaded_files = downloader.download_branch_datasets(max_workers=8)

    # Procesar datasets descargados
    downloader.process_downloaded_datasets(downloaded_files)


if __name__ == "__main__":
    main()
