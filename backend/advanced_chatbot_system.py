#!/usr/bin/env python3
"""
Sistema Avanzado de Chatbot Sheily AI
=====================================
Chatbot con acceso completo a todos los módulos, ramas y funcionalidades del proyecto
"""

import os
import json
import logging
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import subprocess
import psutil
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheilyAdvancedChatbot:
    """Sistema avanzado de chatbot con acceso completo al proyecto"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.modules_dir = self.project_root / "modules"
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.branches_dir = self.project_root / "data" / "branches"
        self.llm_server_url = "http://localhost:8005"
        
        # Cargar configuraciones
        self.load_project_config()
        self.load_branches_config()
        self.load_modules_info()
        
        logger.info("🤖 Sistema Avanzado de Chatbot Sheily AI inicializado")
    
    def load_project_config(self):
        """Cargar configuración del proyecto"""
        try:
            config_files = [
                "unified_config.json",
                "neurofusion_config.json",
                "branch_config.json"
            ]
            
            self.project_config = {}
            for config_file in config_files:
                config_path = self.config_dir / config_file
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self.project_config[config_file.replace('.json', '')] = json.load(f)
            
            logger.info(f"✅ Configuraciones cargadas: {list(self.project_config.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            self.project_config = {}
    
    def load_branches_config(self):
        """Cargar configuración de ramas"""
        try:
            branches_file = self.project_root / "data" / "branches" / "base_branches.json"
            if branches_file.exists():
                with open(branches_file, 'r', encoding='utf-8') as f:
                    self.branches_config = json.load(f)
            else:
                self.branches_config = {"domains": []}
            
            logger.info(f"✅ {len(self.branches_config.get('domains', []))} ramas cargadas")
            
        except Exception as e:
            logger.error(f"❌ Error cargando ramas: {e}")
            self.branches_config = {"domains": []}
    
    def load_modules_info(self):
        """Cargar información de todos los módulos"""
        try:
            self.modules_info = {}
            
            # Escanear directorio de módulos
            for module_path in self.modules_dir.rglob("*.py"):
                if module_path.name != "__init__.py":
                    relative_path = module_path.relative_to(self.modules_dir)
                    module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
                    
                    # Leer información básica del módulo
                    try:
                        with open(module_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        self.modules_info[module_name] = {
                            "path": str(module_path),
                            "relative_path": str(relative_path),
                            "size": len(content),
                            "lines": len(content.split('\n')),
                            "has_docstring": '"""' in content[:200] or "'''" in content[:200],
                            "functions": self.extract_functions(content),
                            "classes": self.extract_classes(content),
                            "imports": self.extract_imports(content)
                        }
                    except Exception as e:
                        logger.warning(f"⚠️ Error leyendo módulo {module_name}: {e}")
            
            logger.info(f"✅ {len(self.modules_info)} módulos analizados")
            
        except Exception as e:
            logger.error(f"❌ Error cargando módulos: {e}")
            self.modules_info = {}
    
    def extract_functions(self, content: str) -> List[str]:
        """Extraer nombres de funciones del código"""
        import re
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        return functions
    
    def extract_classes(self, content: str) -> List[str]:
        """Extraer nombres de clases del código"""
        import re
        classes = re.findall(r'class\s+(\w+)', content)
        return classes
    
    def extract_imports(self, content: str) -> List[str]:
        """Extraer imports del código"""
        import re
        imports = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', content)
        return [imp[0] or imp[1] for imp in imports]
    
    async def read_file_content(self, file_path: str, max_lines: int = 100) -> Dict[str, Any]:
        """Leer contenido de un archivo"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return {"error": f"Archivo no encontrado: {file_path}"}
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            lines = content.split('\n')
            return {
                "path": str(full_path),
                "size": len(content),
                "lines": len(lines),
                "content": content if len(lines) <= max_lines else '\n'.join(lines[:max_lines]) + f"\n... (truncado, {len(lines)} líneas totales)",
                "extension": full_path.suffix,
                "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error leyendo archivo: {e}"}
    
    async def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """Listar contenido de un directorio"""
        try:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                return {"error": f"Directorio no encontrado: {dir_path}"}
            
            if not full_path.is_dir():
                return {"error": f"No es un directorio: {dir_path}"}
            
            items = []
            for item in full_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return {
                "path": str(full_path),
                "items": sorted(items, key=lambda x: (x["type"], x["name"])),
                "total_items": len(items)
            }
            
        except Exception as e:
            return {"error": f"Error listando directorio: {e}"}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        try:
            # Estado de procesos
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower() or 'node' in proc.info['name'].lower():
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Estado de puertos
            ports_status = {}
            for port in [8000, 8005, 5432]:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', port))
                    ports_status[port] = "open" if result == 0 else "closed"
                    sock.close()
                except:
                    ports_status[port] = "unknown"
            
            # Estado de archivos importantes
            important_files = [
                "backend/config.env",
                "models/llama/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "data/branches/base_branches.json"
            ]
            
            files_status = {}
            for file_path in important_files:
                full_path = self.project_root / file_path
                files_status[file_path] = {
                    "exists": full_path.exists(),
                    "size": full_path.stat().st_size if full_path.exists() else 0
                }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "processes": processes,
                "ports": ports_status,
                "files": files_status,
                "modules_count": len(self.modules_info),
                "branches_count": len(self.branches_config.get('domains', [])),
                "project_size": self.get_project_size()
            }
            
        except Exception as e:
            return {"error": f"Error obteniendo estado: {e}"}
    
    def get_project_size(self) -> Dict[str, Any]:
        """Calcular tamaño del proyecto"""
        try:
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(self.project_root):
                dir_count += len(dirs)
                for file in files:
                    file_path = Path(root) / file
                    if file_path.exists():
                        total_size += file_path.stat().st_size
                        file_count += 1
            
            return {
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "directory_count": dir_count
            }
            
        except Exception as e:
            return {"error": f"Error calculando tamaño: {e}"}
    
    def search_in_code(self, query: str, file_types: List[str] = None) -> Dict[str, Any]:
        """Buscar texto en el código del proyecto"""
        try:
            if file_types is None:
                file_types = ['.py', '.js', '.json', '.md', '.txt']
            
            results = []
            query_lower = query.lower()
            
            for root, dirs, files in os.walk(self.project_root):
                # Excluir directorios innecesarios
                dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'venv', 'env']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in file_types):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query_lower in content.lower():
                                    # Encontrar líneas que contienen la consulta
                                    lines = content.split('\n')
                                    matching_lines = []
                                    for i, line in enumerate(lines, 1):
                                        if query_lower in line.lower():
                                            matching_lines.append({
                                                "line_number": i,
                                                "content": line.strip()
                                            })
                                    
                                    if matching_lines:
                                        results.append({
                                            "file": str(file_path.relative_to(self.project_root)),
                                            "matches": len(matching_lines),
                                            "lines": matching_lines[:5]  # Máximo 5 líneas por archivo
                                        })
                        except Exception as e:
                            logger.warning(f"⚠️ Error leyendo {file_path}: {e}")
            
            return {
                "query": query,
                "total_matches": len(results),
                "results": results[:20]  # Máximo 20 archivos
            }
            
        except Exception as e:
            return {"error": f"Error en búsqueda: {e}"}
    
    def get_branch_info(self, branch_name: str = None) -> Dict[str, Any]:
        """Obtener información de ramas"""
        try:
            if branch_name:
                # Información de una rama específica
                for domain in self.branches_config.get('domains', []):
                    if domain.get('name') == branch_name:
                        return {
                            "branch": domain,
                            "exercises_file": f"data/branches/{branch_name}.jsonl",
                            "has_exercises": (self.project_root / "data" / "branches" / f"{branch_name}.jsonl").exists()
                        }
                return {"error": f"Rama no encontrada: {branch_name}"}
            else:
                # Lista de todas las ramas
                branches = []
                for domain in self.branches_config.get('domains', []):
                    branch_name = domain.get('name')
                    exercises_file = self.project_root / "data" / "branches" / f"{branch_name}.jsonl"
                    branches.append({
                        "name": branch_name,
                        "description": domain.get('description', ''),
                        "keywords": domain.get('keywords', []),
                        "has_exercises": exercises_file.exists(),
                        "exercises_count": len(exercises_file.read_text().split('\n')) - 1 if exercises_file.exists() else 0
                    })
                
                return {
                    "total_branches": len(branches),
                    "branches": branches
                }
                
        except Exception as e:
            return {"error": f"Error obteniendo información de ramas: {e}"}
    
    def execute_module_function(self, module_name: str, function_name: str, args: List[Any] = None) -> Dict[str, Any]:
        """Ejecutar función de un módulo"""
        try:
            # Importar módulo dinámicamente
            import importlib.util
            import sys
            
            module_path = self.modules_dir / f"{module_name}.py"
            if not module_path.exists():
                return {"error": f"Módulo no encontrado: {module_name}"}
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Verificar que la función existe
            if not hasattr(module, function_name):
                return {"error": f"Función no encontrada: {function_name} en {module_name}"}
            
            # Ejecutar función
            func = getattr(module, function_name)
            if args:
                result = func(*args)
            else:
                result = func()
            
            return {
                "module": module_name,
                "function": function_name,
                "result": str(result),
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Error ejecutando función: {e}"}
    
    async def chat_with_llm(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Chat con el LLM incluyendo contexto del proyecto"""
        try:
            # Preparar mensaje con contexto
            full_message = message
            
            if context:
                context_info = f"\n\nCONTEXTO DEL PROYECTO SHEILY AI:\n"
                if context.get('current_file'):
                    context_info += f"- Archivo actual: {context['current_file']}\n"
                if context.get('current_module'):
                    context_info += f"- Módulo actual: {context['current_module']}\n"
                if context.get('current_branch'):
                    context_info += f"- Rama actual: {context['current_branch']}\n"
                if context.get('system_status'):
                    context_info += f"- Estado del sistema: {context['system_status']}\n"
                
                full_message += context_info
            
            # Llamar al LLM
            response = requests.post(
                f"{self.llm_server_url}/chat",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": full_message
                        }
                    ],
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                llm_response = response.json()
                return {
                    "success": True,
                    "response": llm_response.get("response", ""),
                    "model": llm_response.get("model", ""),
                    "processing_time": llm_response.get("processing_time", 0),
                    "usage": llm_response.get("usage", {})
                }
            else:
                return {"error": f"Error del LLM: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Error comunicándose con LLM: {e}"}

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Instancia global del chatbot
chatbot = SheilyAdvancedChatbot()

@app.route('/api/chatbot/chat', methods=['POST'])
async def chat():
    """Endpoint principal de chat"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', {})
        
        # Procesar comando especial si es necesario
        if message.startswith('/'):
            result = await process_special_command(message, context)
        else:
            result = await chatbot.chat_with_llm(message, context)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error en chat: {e}"}), 500

@app.route('/api/chatbot/read-file', methods=['POST'])
async def read_file():
    """Leer archivo del proyecto"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        max_lines = data.get('max_lines', 100)
        
        result = await chatbot.read_file_content(file_path, max_lines)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error leyendo archivo: {e}"}), 500

@app.route('/api/chatbot/list-dir', methods=['POST'])
async def list_directory():
    """Listar directorio del proyecto"""
    try:
        data = request.get_json()
        dir_path = data.get('dir_path', '')
        
        result = await chatbot.list_directory(dir_path)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error listando directorio: {e}"}), 500

@app.route('/api/chatbot/system-status', methods=['GET'])
def system_status():
    """Obtener estado del sistema"""
    try:
        result = chatbot.get_system_status()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo estado: {e}"}), 500

@app.route('/api/chatbot/search', methods=['POST'])
def search_code():
    """Buscar en el código"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        file_types = data.get('file_types', ['.py', '.js', '.json'])
        
        result = chatbot.search_in_code(query, file_types)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error en búsqueda: {e}"}), 500

@app.route('/api/chatbot/branches', methods=['GET'])
def get_branches():
    """Obtener información de ramas"""
    try:
        branch_name = request.args.get('branch')
        result = chatbot.get_branch_info(branch_name)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo ramas: {e}"}), 500

@app.route('/api/chatbot/modules', methods=['GET'])
def get_modules():
    """Obtener información de módulos"""
    try:
        return jsonify({
            "total_modules": len(chatbot.modules_info),
            "modules": chatbot.modules_info
        })
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo módulos: {e}"}), 500

@app.route('/api/chatbot/execute', methods=['POST'])
def execute_function():
    """Ejecutar función de módulo"""
    try:
        data = request.get_json()
        module_name = data.get('module_name', '')
        function_name = data.get('function_name', '')
        args = data.get('args', [])
        
        result = chatbot.execute_module_function(module_name, function_name, args)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error ejecutando función: {e}"}), 500

async def process_special_command(command: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar comandos especiales del chatbot"""
    try:
        parts = command[1:].split()
        cmd = parts[0].lower()
        
        if cmd == "status":
            return {"success": True, "response": f"Estado del sistema: {chatbot.get_system_status()}"}
        
        elif cmd == "branches":
            branch_info = chatbot.get_branch_info()
            return {"success": True, "response": f"Ramas disponibles: {branch_info}"}
        
        elif cmd == "modules":
            return {"success": True, "response": f"Módulos disponibles: {len(chatbot.modules_info)} módulos cargados"}
        
        elif cmd == "read" and len(parts) > 1:
            file_path = parts[1]
            file_content = await chatbot.read_file_content(file_path)
            return {"success": True, "response": f"Contenido del archivo {file_path}: {file_content}"}
        
        elif cmd == "list" and len(parts) > 1:
            dir_path = parts[1]
            dir_content = await chatbot.list_directory(dir_path)
            return {"success": True, "response": f"Contenido del directorio {dir_path}: {dir_content}"}
        
        elif cmd == "search" and len(parts) > 1:
            query = " ".join(parts[1:])
            search_results = chatbot.search_in_code(query)
            return {"success": True, "response": f"Resultados de búsqueda para '{query}': {search_results}"}
        
        else:
            return {"success": True, "response": f"Comando no reconocido: {cmd}. Comandos disponibles: /status, /branches, /modules, /read <archivo>, /list <directorio>, /search <texto>"}
            
    except Exception as e:
        return {"error": f"Error procesando comando: {e}"}

if __name__ == "__main__":
    print("🚀 Iniciando Sistema Avanzado de Chatbot Sheily AI...")
    print("📡 Servidor disponible en: http://localhost:8001")
    print("🤖 Endpoints disponibles:")
    print("   - POST /api/chatbot/chat - Chat principal")
    print("   - POST /api/chatbot/read-file - Leer archivos")
    print("   - POST /api/chatbot/list-dir - Listar directorios")
    print("   - GET /api/chatbot/system-status - Estado del sistema")
    print("   - POST /api/chatbot/search - Buscar en código")
    print("   - GET /api/chatbot/branches - Información de ramas")
    print("   - GET /api/chatbot/modules - Información de módulos")
    print("   - POST /api/chatbot/execute - Ejecutar funciones")
    
    app.run(host='0.0.0.0', port=8001, debug=True)
