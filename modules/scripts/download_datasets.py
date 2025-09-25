import os
import logging
import requests
import json
import zipfile
import tarfile
from typing import Dict, List, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


class DatasetDownloader:
    def __init__(
        self,
        output_dir: str = "datasets/external",
        config_path: str = "utils/data_sources.yaml",
    ):
        """
        Inicializar descargador de datasets

        Args:
            output_dir (str): Directorio de salida para datasets
            config_path (str): Ruta al archivo de configuración de fuentes
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Directorios
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Cargar configuración de fuentes
        with open(config_path, "r") as f:
            self.sources = json.load(f)

    def _download_file(
        self, url: str, domain: str, max_retries: int = 3
    ) -> Optional[str]:
        """
        Descargar archivo desde URL

        Args:
            url (str): URL del archivo
            domain (str): Dominio asociado
            max_retries (int): Número máximo de reintentos

        Returns:
            Ruta del archivo descargado o None
        """
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        # Crear subdirectorio para el dominio
        domain_dir = os.path.join(self.output_dir, domain.lower().replace(" ", "_"))
        os.makedirs(domain_dir, exist_ok=True)

        filepath = os.path.join(domain_dir, filename)

        for attempt in range(max_retries):
            try:
                with requests.get(url, stream=True, timeout=30) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get("content-length", 0))

                    with open(filepath, "wb") as f, tqdm(
                        desc=f"Descargando {filename}",
                        total=total_size,
                        unit="iB",
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as progress_bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            size = f.write(chunk)
                            progress_bar.update(size)

                return filepath

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Error descargando {url}: {e}")
                if attempt == max_retries - 1:
                    return None

    def _extract_archive(self, filepath: str, domain: str) -> List[str]:
        """
        Extraer archivos comprimidos

        Args:
            filepath (str): Ruta del archivo comprimido
            domain (str): Dominio asociado

        Returns:
            Lista de archivos extraídos
        """
        domain_dir = os.path.join(self.output_dir, domain.lower().replace(" ", "_"))
        extracted_files = []

        try:
            if filepath.endswith(".zip"):
                with zipfile.ZipFile(filepath, "r") as zip_ref:
                    zip_ref.extractall(domain_dir)
                    extracted_files = zip_ref.namelist()

            elif filepath.endswith((".tar.gz", ".tgz")):
                with tarfile.open(filepath, "r:gz") as tar_ref:
                    tar_ref.extractall(domain_dir)
                    extracted_files = tar_ref.getnames()

            else:
                self.logger.warning(f"Formato no soportado: {filepath}")

        except Exception as e:
            self.logger.error(f"Error extrayendo {filepath}: {e}")

        return extracted_files

    def download_domain_datasets(
        self, domains: Optional[List[str]] = None, max_workers: int = 4
    ) -> Dict[str, List[str]]:
        """
        Descargar datasets para dominios específicos

        Args:
            domains (list, opcional): Lista de dominios a descargar
            max_workers (int): Número máximo de descargas concurrentes

        Returns:
            Diccionario con archivos descargados por dominio
        """
        # Si no se especifican dominios, descargar todos
        if domains is None:
            domains = list(self.sources.keys())

        downloaded_files = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for domain in domains:
                domain_sources = self.sources.get(domain, [])

                for source in domain_sources:
                    future = executor.submit(self._download_file, source["url"], domain)
                    futures[future] = (domain, source)

            for future in tqdm(
                as_completed(futures), total=len(futures), desc="Descargando datasets"
            ):
                domain, source = futures[future]
                filepath = future.result()

                if filepath:
                    # Intentar extraer si es un archivo comprimido
                    extracted_files = self._extract_archive(filepath, domain)

                    if domain not in downloaded_files:
                        downloaded_files[domain] = []

                    downloaded_files[domain].extend(extracted_files or [filepath])

        return downloaded_files

    def validate_datasets(
        self, downloaded_files: Dict[str, List[str]]
    ) -> Dict[str, bool]:
        """
        Validar integridad de datasets descargados

        Args:
            downloaded_files (dict): Archivos descargados por dominio

        Returns:
            Diccionario de validación por dominio
        """
        validation_results = {}

        for domain, files in downloaded_files.items():
            domain_valid = True

            for filepath in files:
                # Verificaciones básicas
                if not os.path.exists(filepath):
                    domain_valid = False
                    self.logger.warning(f"Archivo no encontrado: {filepath}")

                if os.path.getsize(filepath) == 0:
                    domain_valid = False
                    self.logger.warning(f"Archivo vacío: {filepath}")

            validation_results[domain] = domain_valid

        return validation_results


def main():
    """Ejemplo de uso del descargador de datasets"""
    downloader = DatasetDownloader()

    # Descargar datasets de dominios específicos
    downloaded_files = downloader.download_domain_datasets(
        domains=["Medicina y Salud", "Matemáticas", "Computación y Programación"]
    )

    # Validar datasets descargados
    validation_results = downloader.validate_datasets(downloaded_files)

    # Mostrar resultados
    for domain, is_valid in validation_results.items():
        print(f"Dominio {domain}: {'Válido' if is_valid else 'Inválido'}")


if __name__ == "__main__":
    main()
