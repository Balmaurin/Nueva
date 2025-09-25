#!/usr/bin/env python3
"""
Gestor de Pruebas End-to-End del Sistema NeuroFusion
Maneja la ejecución, configuración y reportes de todas las pruebas E2E
"""

import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import yaml

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Resultado de una prueba E2E"""

    test_name: str
    test_type: str
    success: bool
    execution_time: float
    error_message: Optional[str]
    screenshots: List[str]
    logs: List[str]
    api_calls: List[Dict[str, Any]]
    browser_console: List[str]
    performance_metrics: Dict[str, Any]


@dataclass
class TestSuite:
    """Suite de pruebas E2E"""

    name: str
    description: str
    tests: List[str]
    timeout: int
    retries: int
    parallel: bool
    dependencies: List[str]


@dataclass
class E2EConfig:
    """Configuración de pruebas E2E"""

    base_url: str
    api_url: str
    browser: str
    headless: bool
    timeout: int
    retries: int
    parallel_workers: int
    screenshots_on_failure: bool
    video_recording: bool
    trace_recording: bool


class E2ETestManager:
    """Gestor principal de pruebas end-to-end del sistema NeuroFusion"""

    def __init__(self, e2e_dir: str = "e2e"):
        self.e2e_dir = Path(e2e_dir)
        self.test_results = []
        self.test_suites = {}
        self.config = None
        self.test_runner = None

        # Inicializar directorios
        self._initialize_directories()

        # Cargar configuración
        self._load_configuration()

        # Cargar suites de pruebas
        self._load_test_suites()

    def _initialize_directories(self):
        """Inicializa los directorios necesarios"""
        directories = [
            self.e2e_dir,
            self.e2e_dir / "tests",
            self.e2e_dir / "config",
            self.e2e_dir / "reports",
            self.e2e_dir / "screenshots",
            self.e2e_dir / "videos",
            self.e2e_dir / "traces",
            self.e2e_dir / "logs",
            self.e2e_dir / "fixtures",
            self.e2e_dir / "utils",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio inicializado: {directory}")

    def _load_configuration(self):
        """Carga la configuración de pruebas E2E"""
        config_file = self.e2e_dir / "config" / "e2e_config.json"

        if config_file.exists():
            with open(config_file, "r") as f:
                config_data = json.load(f)
        else:
            # Configuración por defecto
            config_data = {
                "base_url": "http://127.0.0.1:3000",
                "api_url": "http://127.0.0.1:8000",
                "browser": "chromium",
                "headless": True,
                "timeout": 30000,
                "retries": 3,
                "parallel_workers": 4,
                "screenshots_on_failure": True,
                "video_recording": True,
                "trace_recording": True,
                "test_credentials": {
                    "test_user": "testuser_e2e",
                    "test_email": "test_e2e@example.com",
                    "test_password": "testpassword123",
                },
                "api_endpoints": {
                    "auth": "/api/auth",
                    "chat": "/api/chat",
                    "training": "/api/training",
                    "vault": "/api/vault",
                    "user": "/api/user",
                },
            }

            # Guardar configuración por defecto
            with open(config_file, "w") as f:
                json.dump(config_data, f, indent=2)

        self.config = E2EConfig(**config_data)
        logger.info(f"Configuración E2E cargada: {self.config}")

    def _load_test_suites(self):
        """Carga las suites de pruebas"""
        suites_file = self.e2e_dir / "config" / "test_suites.json"

        if suites_file.exists():
            with open(suites_file, "r") as f:
                suites_data = json.load(f)
        else:
            # Suites por defecto
            suites_data = {
                "authentication": {
                    "name": "Authentication Tests",
                    "description": "Pruebas de autenticación y registro",
                    "tests": [
                        "test_user_registration",
                        "test_user_login",
                        "test_session_persistence",
                        "test_logout",
                        "test_password_reset",
                    ],
                    "timeout": 30000,
                    "retries": 2,
                    "parallel": False,
                    "dependencies": [],
                },
                "chat_interaction": {
                    "name": "Chat Interaction Tests",
                    "description": "Pruebas de interacción con el chat IA",
                    "tests": [
                        "test_chat_message_send",
                        "test_chat_response_receive",
                        "test_chat_history",
                        "test_chat_error_handling",
                        "test_chat_rate_limiting",
                    ],
                    "timeout": 45000,
                    "retries": 3,
                    "parallel": True,
                    "dependencies": ["authentication"],
                },
                "training_system": {
                    "name": "Training System Tests",
                    "description": "Pruebas del sistema de entrenamiento",
                    "tests": [
                        "test_training_session_start",
                        "test_exercise_completion",
                        "test_progress_tracking",
                        "test_training_metrics",
                        "test_training_error_handling",
                    ],
                    "timeout": 60000,
                    "retries": 2,
                    "parallel": True,
                    "dependencies": ["authentication"],
                },
                "vault_system": {
                    "name": "Vault System Tests",
                    "description": "Pruebas del sistema de caja fuerte",
                    "tests": [
                        "test_vault_statistics",
                        "test_balance_display",
                        "test_experience_tracking",
                        "test_level_progression",
                        "test_vault_security",
                    ],
                    "timeout": 30000,
                    "retries": 2,
                    "parallel": False,
                    "dependencies": ["authentication"],
                },
                "api_integration": {
                    "name": "API Integration Tests",
                    "description": "Pruebas de integración con APIs",
                    "tests": [
                        "test_api_authentication",
                        "test_api_chat_endpoint",
                        "test_api_training_endpoint",
                        "test_api_vault_endpoint",
                        "test_api_error_handling",
                    ],
                    "timeout": 30000,
                    "retries": 3,
                    "parallel": True,
                    "dependencies": [],
                },
                "performance": {
                    "name": "Performance Tests",
                    "description": "Pruebas de rendimiento y carga",
                    "tests": [
                        "test_page_load_performance",
                        "test_api_response_time",
                        "test_concurrent_users",
                        "test_memory_usage",
                        "test_cpu_usage",
                    ],
                    "timeout": 120000,
                    "retries": 1,
                    "parallel": True,
                    "dependencies": ["authentication"],
                },
                "error_handling": {
                    "name": "Error Handling Tests",
                    "description": "Pruebas de manejo de errores",
                    "tests": [
                        "test_network_errors",
                        "test_api_errors",
                        "test_form_validation",
                        "test_invalid_inputs",
                        "test_timeout_handling",
                    ],
                    "timeout": 30000,
                    "retries": 2,
                    "parallel": False,
                    "dependencies": [],
                },
            }

            # Guardar suites por defecto
            with open(suites_file, "w") as f:
                json.dump(suites_data, f, indent=2)

        for suite_name, suite_data in suites_data.items():
            self.test_suites[suite_name] = TestSuite(**suite_data)

        logger.info(f"Suites de pruebas cargadas: {len(self.test_suites)}")

    def check_environment(self) -> Dict[str, bool]:
        """Verifica que el entorno esté listo para las pruebas"""
        environment_status = {}

        try:
            # Verificar Node.js
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            environment_status["nodejs"] = result.returncode == 0

            # Verificar npm
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True
            )
            environment_status["npm"] = result.returncode == 0

            # Verificar Playwright
            result = subprocess.run(
                ["npx", "playwright", "--version"], capture_output=True, text=True
            )
            environment_status["playwright"] = result.returncode == 0

            # Verificar frontend (puerto 3000)
            try:
                response = requests.get(f"{self.config.base_url}/health", timeout=5)
                environment_status["frontend"] = response.status_code == 200
            except:
                environment_status["frontend"] = False

            # Verificar backend (puerto 8000)
            try:
                response = requests.get(f"{self.config.api_url}/health", timeout=5)
                environment_status["backend"] = response.status_code == 200
            except:
                environment_status["backend"] = False

            # Verificar navegadores
            browsers = ["chromium", "firefox", "webkit"]
            for browser in browsers:
                result = subprocess.run(
                    ["npx", "playwright", "install", browser],
                    capture_output=True,
                    text=True,
                )
                environment_status[f"browser_{browser}"] = result.returncode == 0

            logger.info(f"Estado del entorno: {environment_status}")
            return environment_status

        except Exception as e:
            logger.error(f"Error verificando entorno: {e}")
            return environment_status

    def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Ejecuta una suite de pruebas específica"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Suite de pruebas no encontrada: {suite_name}")

        suite = self.test_suites[suite_name]
        logger.info(f"Ejecutando suite: {suite.name}")

        results = []

        try:
            # Verificar dependencias
            for dependency in suite.dependencies:
                if dependency in self.test_suites:
                    logger.info(f"Ejecutando dependencia: {dependency}")
                    dep_results = self.run_test_suite(dependency)
                    results.extend(dep_results)

            # Ejecutar pruebas de la suite
            if suite.parallel:
                results.extend(self._run_tests_parallel(suite))
            else:
                results.extend(self._run_tests_sequential(suite))

            logger.info(f"Suite {suite.name} completada: {len(results)} resultados")
            return results

        except Exception as e:
            logger.error(f"Error ejecutando suite {suite_name}: {e}")
            return results

    def _run_tests_sequential(self, suite: TestSuite) -> List[TestResult]:
        """Ejecuta pruebas de forma secuencial"""
        results = []

        for test_name in suite.tests:
            for attempt in range(suite.retries + 1):
                try:
                    logger.info(
                        f"Ejecutando prueba: {test_name} (intento {attempt + 1})"
                    )

                    start_time = time.time()
                    result = self._execute_single_test(test_name, suite.timeout)
                    execution_time = time.time() - start_time

                    result.execution_time = execution_time
                    results.append(result)

                    if result.success:
                        logger.info(f"Prueba {test_name} exitosa")
                        break
                    else:
                        logger.warning(
                            f"Prueba {test_name} falló (intento {attempt + 1})"
                        )
                        if attempt < suite.retries:
                            time.sleep(2)  # Esperar antes del reintento

                except Exception as e:
                    logger.error(f"Error ejecutando prueba {test_name}: {e}")
                    result = TestResult(
                        test_name=test_name,
                        test_type=suite.name,
                        success=False,
                        execution_time=0,
                        error_message=str(e),
                        screenshots=[],
                        logs=[],
                        api_calls=[],
                        browser_console=[],
                        performance_metrics={},
                    )
                    results.append(result)

        return results

    def _run_tests_parallel(self, suite: TestSuite) -> List[TestResult]:
        """Ejecuta pruebas en paralelo"""
        results = []

        with ThreadPoolExecutor(max_workers=self.config.parallel_workers) as executor:
            futures = []

            for test_name in suite.tests:
                future = executor.submit(
                    self._execute_test_with_retries, test_name, suite
                )
                futures.append((test_name, future))

            for test_name, future in futures:
                try:
                    result = future.result(timeout=suite.timeout / 1000)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error en prueba paralela {test_name}: {e}")
                    result = TestResult(
                        test_name=test_name,
                        test_type=suite.name,
                        success=False,
                        execution_time=0,
                        error_message=str(e),
                        screenshots=[],
                        logs=[],
                        api_calls=[],
                        browser_console=[],
                        performance_metrics={},
                    )
                    results.append(result)

        return results

    def _execute_test_with_retries(
        self, test_name: str, suite: TestSuite
    ) -> TestResult:
        """Ejecuta una prueba con reintentos"""
        for attempt in range(suite.retries + 1):
            try:
                start_time = time.time()
                result = self._execute_single_test(test_name, suite.timeout)
                execution_time = time.time() - start_time

                result.execution_time = execution_time

                if result.success:
                    return result
                else:
                    logger.warning(f"Prueba {test_name} falló (intento {attempt + 1})")
                    if attempt < suite.retries:
                        time.sleep(2)

            except Exception as e:
                logger.error(
                    f"Error en prueba {test_name} (intento {attempt + 1}): {e}"
                )
                if attempt == suite.retries:
                    return TestResult(
                        test_name=test_name,
                        test_type=suite.name,
                        success=False,
                        execution_time=0,
                        error_message=str(e),
                        screenshots=[],
                        logs=[],
                        api_calls=[],
                        browser_console=[],
                        performance_metrics={},
                    )

        return TestResult(
            test_name=test_name,
            test_type=suite.name,
            success=False,
            execution_time=0,
            error_message="Máximo de reintentos alcanzado",
            screenshots=[],
            logs=[],
            api_calls=[],
            browser_console=[],
            performance_metrics={},
        )

    def _execute_single_test(self, test_name: str, timeout: int) -> TestResult:
        """Ejecuta una prueba individual"""
        try:
            # Construir comando de Playwright
            cmd = [
                "npx",
                "playwright",
                "test",
                "--project",
                self.config.browser,
                "--timeout",
                str(timeout),
                "--reporter",
                "json",
            ]

            if self.config.headless:
                cmd.append("--headed=false")

            if self.config.screenshots_on_failure:
                cmd.extend(["--screenshot", "on"])

            if self.config.video_recording:
                cmd.extend(["--video", "on"])

            if self.config.trace_recording:
                cmd.extend(["--trace", "on"])

            # Agregar filtro de prueba específica
            cmd.extend(["--grep", test_name])

            # Ejecutar comando
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.e2e_dir,
                timeout=timeout / 1000,
            )

            # Procesar resultado
            success = result.returncode == 0
            error_message = result.stderr if not success else None

            # Extraer información adicional
            screenshots = self._extract_screenshots(test_name)
            logs = self._extract_logs(test_name)
            api_calls = self._extract_api_calls(test_name)
            browser_console = self._extract_browser_console(test_name)
            performance_metrics = self._extract_performance_metrics(test_name)

            return TestResult(
                test_name=test_name,
                test_type="e2e",
                success=success,
                execution_time=0,  # Se establece después
                error_message=error_message,
                screenshots=screenshots,
                logs=logs,
                api_calls=api_calls,
                browser_console=browser_console,
                performance_metrics=performance_metrics,
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=test_name,
                test_type="e2e",
                success=False,
                execution_time=timeout / 1000,
                error_message="Timeout en ejecución",
                screenshots=[],
                logs=[],
                api_calls=[],
                browser_console=[],
                performance_metrics={},
            )
        except Exception as e:
            return TestResult(
                test_name=test_name,
                test_type="e2e",
                success=False,
                execution_time=0,
                error_message=str(e),
                screenshots=[],
                logs=[],
                api_calls=[],
                browser_console=[],
                performance_metrics={},
            )

    def _extract_screenshots(self, test_name: str) -> List[str]:
        """Extrae screenshots de una prueba"""
        screenshots = []
        screenshots_dir = self.e2e_dir / "screenshots"

        if screenshots_dir.exists():
            for screenshot_file in screenshots_dir.glob(f"*{test_name}*"):
                screenshots.append(str(screenshot_file))

        return screenshots

    def _extract_logs(self, test_name: str) -> List[str]:
        """Extrae logs de una prueba"""
        logs = []
        logs_dir = self.e2e_dir / "logs"

        if logs_dir.exists():
            log_file = logs_dir / f"{test_name}.log"
            if log_file.exists():
                with open(log_file, "r") as f:
                    logs = f.readlines()

        return logs

    def _extract_api_calls(self, test_name: str) -> List[Dict[str, Any]]:
        """Extrae llamadas a API de una prueba"""
        api_calls = []
        traces_dir = self.e2e_dir / "traces"

        if traces_dir.exists():
            trace_file = traces_dir / f"{test_name}.zip"
            if trace_file.exists():
                # Aquí se procesaría el archivo de trace para extraer llamadas API
                # Por simplicidad, retornamos una lista vacía
                pass

        return api_calls

    def _extract_browser_console(self, test_name: str) -> List[str]:
        """Extrae logs de consola del navegador"""
        console_logs = []
        logs_dir = self.e2e_dir / "logs"

        if logs_dir.exists():
            console_file = logs_dir / f"{test_name}_console.log"
            if console_file.exists():
                with open(console_file, "r") as f:
                    console_logs = f.readlines()

        return console_logs

    def _extract_performance_metrics(self, test_name: str) -> Dict[str, Any]:
        """Extrae métricas de rendimiento de una prueba"""
        metrics = {}
        reports_dir = self.e2e_dir / "reports"

        if reports_dir.exists():
            metrics_file = reports_dir / f"{test_name}_metrics.json"
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    metrics = json.load(f)

        return metrics

    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Ejecuta todas las suites de pruebas"""
        all_results = {}

        logger.info("Iniciando ejecución de todas las pruebas E2E")

        # Verificar entorno
        environment_status = self.check_environment()
        if not all(environment_status.values()):
            logger.warning("Algunos componentes del entorno no están disponibles")

        # Ejecutar cada suite
        for suite_name in self.test_suites.keys():
            try:
                results = self.run_test_suite(suite_name)
                all_results[suite_name] = results

                # Guardar resultados de la suite
                self._save_suite_results(suite_name, results)

            except Exception as e:
                logger.error(f"Error ejecutando suite {suite_name}: {e}")
                all_results[suite_name] = []

        # Generar reporte general
        self._generate_overall_report(all_results)

        logger.info("Ejecución de todas las pruebas E2E completada")
        return all_results

    def _save_suite_results(self, suite_name: str, results: List[TestResult]):
        """Guarda los resultados de una suite"""
        try:
            reports_dir = self.e2e_dir / "reports"
            reports_dir.mkdir(exist_ok=True)

            # Convertir resultados a diccionarios
            results_data = [asdict(result) for result in results]

            # Guardar como JSON
            report_file = reports_dir / f"{suite_name}_results.json"
            with open(report_file, "w") as f:
                json.dump(
                    {
                        "suite_name": suite_name,
                        "timestamp": datetime.now().isoformat(),
                        "total_tests": len(results),
                        "passed_tests": sum(1 for r in results if r.success),
                        "failed_tests": sum(1 for r in results if not r.success),
                        "results": results_data,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Resultados de suite {suite_name} guardados: {report_file}")

        except Exception as e:
            logger.error(f"Error guardando resultados de suite {suite_name}: {e}")

    def _generate_overall_report(self, all_results: Dict[str, List[TestResult]]):
        """Genera un reporte general de todas las pruebas"""
        try:
            reports_dir = self.e2e_dir / "reports"
            reports_dir.mkdir(exist_ok=True)

            # Calcular estadísticas generales
            total_tests = sum(len(results) for results in all_results.values())
            total_passed = sum(
                sum(1 for r in results if r.success) for results in all_results.values()
            )
            total_failed = total_tests - total_passed

            # Calcular tiempo total de ejecución
            total_time = sum(
                sum(r.execution_time for r in results)
                for results in all_results.values()
            )

            # Generar reporte
            overall_report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_suites": len(all_results),
                    "total_tests": total_tests,
                    "passed_tests": total_passed,
                    "failed_tests": total_failed,
                    "success_rate": (
                        (total_passed / total_tests * 100) if total_tests > 0 else 0
                    ),
                    "total_execution_time": total_time,
                },
                "suite_results": {},
            }

            # Agregar resultados por suite
            for suite_name, results in all_results.items():
                suite_passed = sum(1 for r in results if r.success)
                suite_failed = len(results) - suite_passed
                suite_time = sum(r.execution_time for r in results)

                overall_report["suite_results"][suite_name] = {
                    "total_tests": len(results),
                    "passed_tests": suite_passed,
                    "failed_tests": suite_failed,
                    "success_rate": (
                        (suite_passed / len(results) * 100) if results else 0
                    ),
                    "execution_time": suite_time,
                }

            # Guardar reporte general
            report_file = reports_dir / "overall_e2e_report.json"
            with open(report_file, "w") as f:
                json.dump(overall_report, f, indent=2)

            logger.info(f"Reporte general E2E guardado: {report_file}")

        except Exception as e:
            logger.error(f"Error generando reporte general: {e}")

    def get_test_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las pruebas ejecutadas"""
        if not self.test_results:
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0,
                "total_time": 0,
            }

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        total_time = sum(r.execution_time for r in self.test_results)

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_time": total_time,
            "results": [asdict(r) for r in self.test_results],
        }

    def cleanup_test_artifacts(self) -> int:
        """Limpia artefactos de pruebas antiguos"""
        cleaned_count = 0

        try:
            # Limpiar screenshots antiguos (más de 7 días)
            screenshots_dir = self.e2e_dir / "screenshots"
            if screenshots_dir.exists():
                for screenshot_file in screenshots_dir.glob("*"):
                    if screenshot_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):
                        screenshot_file.unlink()
                        cleaned_count += 1

            # Limpiar videos antiguos
            videos_dir = self.e2e_dir / "videos"
            if videos_dir.exists():
                for video_file in videos_dir.glob("*"):
                    if video_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):
                        video_file.unlink()
                        cleaned_count += 1

            # Limpiar traces antiguos
            traces_dir = self.e2e_dir / "traces"
            if traces_dir.exists():
                for trace_file in traces_dir.glob("*"):
                    if trace_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):
                        trace_file.unlink()
                        cleaned_count += 1

            logger.info(f"Artefactos limpiados: {cleaned_count}")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error limpiando artefactos: {e}")
            return 0


# Instancia global del gestor E2E
e2e_test_manager = E2ETestManager()


def get_e2e_test_manager() -> E2ETestManager:
    """Obtiene la instancia global del gestor de pruebas E2E"""
    return e2e_test_manager


if __name__ == "__main__":
    # Ejemplo de uso
    manager = E2ETestManager()

    # Verificar entorno
    env_status = manager.check_environment()
    print(f"Estado del entorno: {env_status}")

    # Ejecutar todas las pruebas
    results = manager.run_all_tests()

    # Mostrar resumen
    summary = manager.get_test_summary()
    print(
        f"Resumen: {summary['passed_tests']}/{summary['total_tests']} pruebas exitosas"
    )

    # Limpiar artefactos
    manager.cleanup_test_artifacts()
