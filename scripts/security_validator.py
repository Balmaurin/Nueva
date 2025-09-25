#!/usr/bin/env python3
"""
Validador de Seguridad Real para Sheily AI
==========================================
Script que valida la seguridad del proyecto sin simulaciones
"""

import os
import re
import json
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class SecurityValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.vulnerabilities = []
        self.warnings = []
        self.passed_checks = []
    
    def validate_environment_files(self):
        """Validar archivos de entorno"""
        print("🔍 Validando archivos de entorno...")
        
        env_files = [
            ".env",
            ".env.local", 
            ".env.production",
            "config.env",
            "backend/config.env"
        ]
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self.vulnerabilities.append({
                    "type": "CRITICAL",
                    "file": str(env_path),
                    "issue": "Archivo de entorno expuesto en repositorio",
                    "fix": "Mover a .gitignore y usar variables de entorno"
                })
            else:
                self.passed_checks.append(f"✅ {env_file} no está en el repositorio")
    
    def validate_gitignore(self):
        """Validar .gitignore"""
        print("🔍 Validando .gitignore...")
        
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            self.vulnerabilities.append({
                "type": "HIGH",
                "file": ".gitignore",
                "issue": "Archivo .gitignore no existe",
                "fix": "Crear .gitignore con archivos sensibles"
            })
            return
        
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        required_patterns = [
            "*.env",
            "*.key",
            "*.pem",
            "*.db",
            "*.log",
            "node_modules/",
            "__pycache__/",
            "venv/",
            ".next/",
            "backups/",
            "logs/"
        ]
        
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                self.warnings.append({
                    "type": "MEDIUM",
                    "file": ".gitignore",
                    "issue": f"Patrón '{pattern}' no está en .gitignore",
                    "fix": f"Agregar '{pattern}' a .gitignore"
                })
            else:
                self.passed_checks.append(f"✅ Patrón '{pattern}' está en .gitignore")
    
    def validate_hardcoded_secrets(self):
        """Validar secretos hardcodeados"""
        print("🔍 Validando secretos hardcodeados...")
        
        # Patrones de secretos comunes
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'][^"\']+["\']',
            r'jwt_secret\s*=\s*["\'][^"\']+["\']',
        ]
        
        # Archivos a verificar
        code_files = list(self.project_root.rglob("*.py")) + \
                    list(self.project_root.rglob("*.js")) + \
                    list(self.project_root.rglob("*.ts")) + \
                    list(self.project_root.rglob("*.tsx"))
        
        for file_path in code_files:
            # Saltar node_modules y otros directorios
            if any(skip in str(file_path) for skip in ["node_modules", "__pycache__", ".next", ".git"]):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Verificar si es un valor real o una variable
                        if not any(var in match.lower() for var in ["process.env", "os.getenv", "process.env"]):
                            self.vulnerabilities.append({
                                "type": "HIGH",
                                "file": str(file_path),
                                "issue": f"Secreto hardcodeado: {match}",
                                "fix": "Usar variables de entorno"
                            })
            except Exception as e:
                self.warnings.append({
                    "type": "LOW",
                    "file": str(file_path),
                    "issue": f"Error leyendo archivo: {e}",
                    "fix": "Verificar permisos de archivo"
                })
    
    def validate_subprocess_usage(self):
        """Validar uso de subprocess"""
        print("🔍 Validando uso de subprocess...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if any(skip in str(file_path) for skip in ["__pycache__", ".git", "node_modules"]):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar subprocess.run con shell=True
                if "subprocess.run" in content and "shell=True" in content:
                    self.vulnerabilities.append({
                        "type": "HIGH",
                        "file": str(file_path),
                        "issue": "subprocess.run con shell=True detectado",
                        "fix": "Usar lista de argumentos en lugar de shell=True"
                    })
                elif "subprocess.run" in content:
                    self.passed_checks.append(f"✅ {file_path} usa subprocess.run correctamente")
                    
            except Exception as e:
                self.warnings.append({
                    "type": "LOW",
                    "file": str(file_path),
                    "issue": f"Error leyendo archivo: {e}",
                    "fix": "Verificar permisos de archivo"
                })
    
    def validate_dependencies(self):
        """Validar dependencias"""
        print("🔍 Validando dependencias...")
        
        # Verificar package.json
        package_json = self.project_root / "Frontend" / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                # Verificar dependencias conocidas por vulnerabilidades
                vulnerable_deps = [
                    "axios@<1.6.0",
                    "lodash@<4.17.21",
                    "moment@<2.29.4"
                ]
                
                dependencies = package_data.get("dependencies", {})
                for dep, version in dependencies.items():
                    if any(vuln_dep in f"{dep}@{version}" for vuln_dep in vulnerable_deps):
                        self.vulnerabilities.append({
                            "type": "MEDIUM",
                            "file": str(package_json),
                            "issue": f"Dependencia vulnerable: {dep}@{version}",
                            "fix": "Actualizar a versión segura"
                        })
                    else:
                        self.passed_checks.append(f"✅ Dependencia {dep}@{version} parece segura")
                        
            except Exception as e:
                self.warnings.append({
                    "type": "LOW",
                    "file": str(package_json),
                    "issue": f"Error leyendo package.json: {e}",
                    "fix": "Verificar formato JSON"
                })
    
    def generate_report(self):
        """Generar reporte de seguridad"""
        print("\n" + "="*60)
        print("🔒 REPORTE DE SEGURIDAD - SHEILY AI")
        print("="*60)
        
        print(f"\n✅ VERIFICACIONES EXITOSAS: {len(self.passed_checks)}")
        for check in self.passed_checks:
            print(f"  {check}")
        
        print(f"\n⚠️  ADVERTENCIAS: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"  {warning['type']}: {warning['file']} - {warning['issue']}")
            print(f"    💡 Solución: {warning['fix']}")
        
        print(f"\n🚨 VULNERABILIDADES: {len(self.vulnerabilities)}")
        for vuln in self.vulnerabilities:
            print(f"  {vuln['type']}: {vuln['file']} - {vuln['issue']}")
            print(f"    🔧 Solución: {vuln['fix']}")
        
        # Calcular puntuación
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.vulnerabilities)
        if total_checks > 0:
            score = (len(self.passed_checks) / total_checks) * 100
            print(f"\n📊 PUNTUACIÓN DE SEGURIDAD: {score:.1f}/100")
            
            if score >= 90:
                print("🟢 EXCELENTE - Proyecto muy seguro")
            elif score >= 70:
                print("🟡 BUENO - Algunas mejoras recomendadas")
            elif score >= 50:
                print("🟠 REGULAR - Se requieren correcciones")
            else:
                print("🔴 CRÍTICO - Se requieren correcciones urgentes")
        
        return {
            "score": score if total_checks > 0 else 0,
            "vulnerabilities": self.vulnerabilities,
            "warnings": self.warnings,
            "passed_checks": self.passed_checks
        }
    
    def run_all_checks(self):
        """Ejecutar todas las verificaciones"""
        print("🔒 INICIANDO VALIDACIÓN DE SEGURIDAD REAL")
        print("="*50)
        
        self.validate_environment_files()
        self.validate_gitignore()
        self.validate_hardcoded_secrets()
        self.validate_subprocess_usage()
        self.validate_dependencies()
        
        return self.generate_report()

if __name__ == "__main__":
    validator = SecurityValidator()
    report = validator.run_all_checks()
    
    # Salir con código de error si hay vulnerabilidades críticas
    critical_vulns = [v for v in report["vulnerabilities"] if v["type"] == "CRITICAL"]
    if critical_vulns:
        print(f"\n❌ Se encontraron {len(critical_vulns)} vulnerabilidades críticas")
        exit(1)
    else:
        print("\n✅ No se encontraron vulnerabilidades críticas")
        exit(0)
