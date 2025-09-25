#!/usr/bin/env python3
"""
Verificador de Sistema Optimizado para Sheily AI
===============================================
Script optimizado con timeouts reales y sin simulaciones
"""

import os
import sys
import time
import json
import psutil
import requests
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

class OptimizedSystemVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": time.time(),
            "checks": {},
            "errors": [],
            "warnings": [],
            "performance": {}
        }
        self.timeout_seconds = 30  # Timeout real de 30 segundos
    
    def check_with_timeout(self, func, *args, **kwargs):
        """Ejecutar función con timeout real"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=self.timeout_seconds)
            except FutureTimeoutError:
                return {"error": f"Timeout después de {self.timeout_seconds} segundos"}
            except Exception as e:
                return {"error": str(e)}
    
    def verify_frontend_dependencies(self):
        """Verificar dependencias del frontend"""
        print("🔍 Verificando dependencias del frontend...")
        start_time = time.time()
        
        def check_deps():
            frontend_path = self.project_root / "Frontend"
            if not frontend_path.exists():
                return {"error": "Directorio Frontend no encontrado"}
            
            package_json = frontend_path / "package.json"
            if not package_json.exists():
                return {"error": "package.json no encontrado"}
            
            node_modules = frontend_path / "node_modules"
            if not node_modules.exists():
                return {"error": "node_modules no encontrado - ejecutar npm install"}
            
            # Verificar que las dependencias críticas estén instaladas
            critical_deps = ["react", "next", "axios", "lucide-react"]
            missing_deps = []
            
            for dep in critical_deps:
                dep_path = node_modules / dep
                if not dep_path.exists():
                    missing_deps.append(dep)
            
            if missing_deps:
                return {"error": f"Dependencias faltantes: {missing_deps}"}
            
            return {"status": "ok", "dependencies": "installed"}
        
        result = self.check_with_timeout(check_deps)
        self.results["checks"]["frontend_dependencies"] = result
        self.results["performance"]["frontend_deps_time"] = time.time() - start_time
        
        if "error" in result:
            self.results["errors"].append(f"Frontend dependencies: {result['error']}")
        else:
            print("✅ Dependencias del frontend verificadas")
    
    def verify_backend_config(self):
        """Verificar configuración del backend"""
        print("🔍 Verificando configuración del backend...")
        start_time = time.time()
        
        def check_config():
            backend_path = self.project_root / "backend"
            if not backend_path.exists():
                return {"error": "Directorio backend no encontrado"}
            
            # Verificar que no haya config.env expuesto
            config_env = backend_path / "config.env"
            if config_env.exists():
                return {"error": "config.env expuesto - mover a .gitignore"}
            
            # Verificar config.env.example
            config_example = backend_path / "config.env.example"
            if not config_example.exists():
                return {"error": "config.env.example no encontrado"}
            
            # Verificar server.js
            server_js = backend_path / "server.js"
            if not server_js.exists():
                return {"error": "server.js no encontrado"}
            
            return {"status": "ok", "config": "secure"}
        
        result = self.check_with_timeout(check_config)
        self.results["checks"]["backend_config"] = result
        self.results["performance"]["backend_config_time"] = time.time() - start_time
        
        if "error" in result:
            self.results["errors"].append(f"Backend config: {result['error']}")
        else:
            print("✅ Configuración del backend verificada")
    
    def verify_database_structure(self):
        """Verificar estructura de base de datos"""
        print("🔍 Verificando estructura de base de datos...")
        start_time = time.time()
        
        def check_db():
            data_path = self.project_root / "data"
            if not data_path.exists():
                return {"error": "Directorio data no encontrado"}
            
            # Verificar archivos de base de datos
            db_files = [
                "knowledge_base.db",
                "embeddings_sqlite.db", 
                "rag_memory.duckdb",
                "user_data.duckdb",
                "metrics.db"
            ]
            
            existing_dbs = []
            for db_file in db_files:
                db_path = data_path / db_file
                if db_path.exists():
                    existing_dbs.append(db_file)
            
            if not existing_dbs:
                return {"error": "No se encontraron archivos de base de datos"}
            
            return {"status": "ok", "databases": existing_dbs}
        
        result = self.check_with_timeout(check_db)
        self.results["checks"]["database_structure"] = result
        self.results["performance"]["database_time"] = time.time() - start_time
        
        if "error" in result:
            self.results["errors"].append(f"Database structure: {result['error']}")
        else:
            print("✅ Estructura de base de datos verificada")
    
    def verify_branches_implementation(self):
        """Verificar implementación de ramas"""
        print("🔍 Verificando implementación de ramas...")
        start_time = time.time()
        
        def check_branches():
            branches_path = self.project_root / "data" / "branches"
            if not branches_path.exists():
                return {"error": "Directorio data/branches no encontrado"}
            
            # Verificar que existan las 35 ramas
            expected_branches = [f"branch_{i:02d}_dataset.jsonl" for i in range(1, 36)]
            existing_branches = []
            missing_branches = []
            
            for branch_file in expected_branches:
                branch_path = branches_path / branch_file
                if branch_path.exists():
                    existing_branches.append(branch_file)
                else:
                    missing_branches.append(branch_file)
            
            if missing_branches:
                return {"error": f"Ramas faltantes: {missing_branches}"}
            
            return {"status": "ok", "branches": len(existing_branches)}
        
        result = self.check_with_timeout(check_branches)
        self.results["checks"]["branches_implementation"] = result
        self.results["performance"]["branches_time"] = time.time() - start_time
        
        if "error" in result:
            self.results["errors"].append(f"Branches implementation: {result['error']}")
        else:
            print("✅ Implementación de ramas verificada")
    
    def verify_system_resources(self):
        """Verificar recursos del sistema"""
        print("🔍 Verificando recursos del sistema...")
        start_time = time.time()
        
        def check_resources():
            # Verificar memoria disponible
            memory = psutil.virtual_memory()
            if memory.available < 1024 * 1024 * 1024:  # 1GB
                return {"error": f"Memoria insuficiente: {memory.available // (1024*1024)}MB disponibles"}
            
            # Verificar espacio en disco
            disk = psutil.disk_usage('/')
            if disk.free < 5 * 1024 * 1024 * 1024:  # 5GB
                return {"error": f"Espacio en disco insuficiente: {disk.free // (1024*1024*1024)}GB disponibles"}
            
            # Verificar CPU
            cpu_count = psutil.cpu_count()
            if cpu_count < 2:
                return {"error": f"CPU insuficiente: {cpu_count} cores disponibles"}
            
            return {
                "status": "ok",
                "memory_gb": memory.available // (1024*1024*1024),
                "disk_gb": disk.free // (1024*1024*1024),
                "cpu_cores": cpu_count
            }
        
        result = self.check_with_timeout(check_resources)
        self.results["checks"]["system_resources"] = result
        self.results["performance"]["resources_time"] = time.time() - start_time
        
        if "error" in result:
            self.results["warnings"].append(f"System resources: {result['error']}")
        else:
            print("✅ Recursos del sistema verificados")
    
    def verify_network_connectivity(self):
        """Verificar conectividad de red"""
        print("🔍 Verificando conectividad de red...")
        start_time = time.time()
        
        def check_network():
            # Verificar conectividad básica
            try:
                response = requests.get("https://httpbin.org/get", timeout=10)
                if response.status_code != 200:
                    return {"error": f"Conectividad limitada: HTTP {response.status_code}"}
            except requests.RequestException as e:
                return {"error": f"Sin conectividad: {str(e)}"}
            
            return {"status": "ok", "connectivity": "available"}
        
        result = self.check_with_timeout(check_network)
        self.results["checks"]["network_connectivity"] = result
        self.results["performance"]["network_time"] = time.time() - start_time
        
        if "error" in result:
            self.results["warnings"].append(f"Network connectivity: {result['error']}")
        else:
            print("✅ Conectividad de red verificada")
    
    def generate_report(self):
        """Generar reporte final"""
        print("\n" + "="*60)
        print("🔍 REPORTE DE VERIFICACIÓN DEL SISTEMA")
        print("="*60)
        
        total_checks = len(self.results["checks"])
        successful_checks = sum(1 for check in self.results["checks"].values() 
                               if check.get("status") == "ok")
        
        print(f"\n📊 RESUMEN:")
        print(f"  ✅ Verificaciones exitosas: {successful_checks}/{total_checks}")
        print(f"  ⚠️  Advertencias: {len(self.results['warnings'])}")
        print(f"  🚨 Errores: {len(self.results['errors'])}")
        
        if self.results["errors"]:
            print(f"\n🚨 ERRORES CRÍTICOS:")
            for error in self.results["errors"]:
                print(f"  ❌ {error}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  ADVERTENCIAS:")
            for warning in self.results["warnings"]:
                print(f"  ⚠️  {warning}")
        
        print(f"\n⏱️  RENDIMIENTO:")
        for check_name, time_taken in self.results["performance"].items():
            print(f"  {check_name}: {time_taken:.2f}s")
        
        # Calcular puntuación
        if total_checks > 0:
            score = (successful_checks / total_checks) * 100
            print(f"\n📈 PUNTUACIÓN: {score:.1f}/100")
            
            if score >= 90:
                print("🟢 EXCELENTE - Sistema listo para producción")
            elif score >= 70:
                print("🟡 BUENO - Algunas mejoras recomendadas")
            elif score >= 50:
                print("🟠 REGULAR - Se requieren correcciones")
            else:
                print("🔴 CRÍTICO - Se requieren correcciones urgentes")
        
        return self.results
    
    def run_all_checks(self):
        """Ejecutar todas las verificaciones"""
        print("🔍 INICIANDO VERIFICACIÓN OPTIMIZADA DEL SISTEMA")
        print("="*50)
        
        self.verify_frontend_dependencies()
        self.verify_backend_config()
        self.verify_database_structure()
        self.verify_branches_implementation()
        self.verify_system_resources()
        self.verify_network_connectivity()
        
        return self.generate_report()

if __name__ == "__main__":
    verifier = OptimizedSystemVerifier()
    report = verifier.run_all_checks()
    
    # Salir con código de error si hay errores críticos
    if report["errors"]:
        print(f"\n❌ Se encontraron {len(report['errors'])} errores críticos")
        sys.exit(1)
    else:
        print("\n✅ Sistema verificado exitosamente")
        sys.exit(0)
