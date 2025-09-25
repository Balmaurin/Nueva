/**
 * Sistema de Integración de Chatbot Avanzado
 * ==========================================
 * Integra el chatbot avanzado con el backend principal de Sheily AI
 */

const express = require('express');
const axios = require('axios');
const path = require('path');
const fs = require('fs').promises;

class ChatbotIntegration {
    constructor() {
        this.advancedChatbotUrl = 'http://localhost:8001';
        this.llmServerUrl = 'http://localhost:8005';
        this.projectRoot = path.join(__dirname, '..');
        
        console.log('🔗 Sistema de Integración de Chatbot inicializado');
    }

    /**
     * Procesar mensaje del usuario con contexto completo
     */
    async processUserMessage(message, userContext = {}) {
        try {
            console.log(`💬 Procesando mensaje: ${message.substring(0, 100)}...`);
            
            // Determinar si es un comando especial
            if (message.startsWith('/')) {
                return await this.processSpecialCommand(message, userContext);
            }
            
            // Obtener contexto del proyecto
            const projectContext = await this.getProjectContext(userContext);
            
            // Enviar al chatbot avanzado
            const response = await axios.post(`${this.advancedChatbotUrl}/api/chatbot/chat`, {
                message: message,
                context: {
                    ...userContext,
                    ...projectContext
                }
            });
            
            return {
                success: true,
                response: response.data.response,
                model: response.data.model,
                processing_time: response.data.processing_time,
                context_used: true
            };
            
        } catch (error) {
            console.error('❌ Error procesando mensaje:', error.message);
            
            // Fallback al LLM directo
            return await this.fallbackToDirectLLM(message);
        }
    }

    /**
     * Procesar comandos especiales
     */
    async processSpecialCommand(command, userContext) {
        try {
            const parts = command.substring(1).split(' ');
            const cmd = parts[0].toLowerCase();
            
            switch (cmd) {
                case 'status':
                    return await this.getSystemStatus();
                
                case 'branches':
                    return await this.getBranchesInfo(parts[1]);
                
                case 'modules':
                    return await this.getModulesInfo();
                
                case 'read':
                    if (parts[1]) {
                        return await this.readFile(parts[1]);
                    }
                    return { error: 'Especifica un archivo: /read <archivo>' };
                
                case 'list':
                    if (parts[1]) {
                        return await this.listDirectory(parts[1]);
                    }
                    return { error: 'Especifica un directorio: /list <directorio>' };
                
                case 'search':
                    if (parts[1]) {
                        const query = parts.slice(1).join(' ');
                        return await this.searchInCode(query);
                    }
                    return { error: 'Especifica una búsqueda: /search <texto>' };
                
                case 'execute':
                    if (parts[1] && parts[2]) {
                        return await this.executeModuleFunction(parts[1], parts[2], parts.slice(3));
                    }
                    return { error: 'Especifica módulo y función: /execute <módulo> <función> [args...]' };
                
                case 'help':
                    return this.getHelp();
                
                default:
                    return { error: `Comando no reconocido: ${cmd}. Usa /help para ver comandos disponibles.` };
            }
            
        } catch (error) {
            return { error: `Error procesando comando: ${error.message}` };
        }
    }

    /**
     * Obtener contexto del proyecto
     */
    async getProjectContext(userContext) {
        try {
            const context = {
                timestamp: new Date().toISOString(),
                project_root: this.projectRoot
            };
            
            // Estado del sistema
            try {
                const statusResponse = await axios.get(`${this.advancedChatbotUrl}/api/chatbot/system-status`);
                context.system_status = statusResponse.data;
            } catch (e) {
                context.system_status = { error: 'No disponible' };
            }
            
            // Información de ramas
            try {
                const branchesResponse = await axios.get(`${this.advancedChatbotUrl}/api/chatbot/branches`);
                context.branches_info = branchesResponse.data;
            } catch (e) {
                context.branches_info = { error: 'No disponible' };
            }
            
            return context;
            
        } catch (error) {
            console.error('❌ Error obteniendo contexto:', error.message);
            return { error: 'Error obteniendo contexto del proyecto' };
        }
    }

    /**
     * Fallback al LLM directo
     */
    async fallbackToDirectLLM(message) {
        try {
            console.log('🔄 Usando fallback al LLM directo...');
            
            const response = await axios.post(`${this.llmServerUrl}/chat`, {
                messages: [
                    {
                        role: 'user',
                        content: message
                    }
                ],
                max_tokens: 500
            });
            
            return {
                success: true,
                response: response.data.response,
                model: response.data.model,
                processing_time: response.data.processing_time,
                fallback: true
            };
            
        } catch (error) {
            return {
                error: `Error en fallback: ${error.message}`,
                fallback: true
            };
        }
    }

    /**
     * Obtener estado del sistema
     */
    async getSystemStatus() {
        try {
            const response = await axios.get(`${this.advancedChatbotUrl}/api/chatbot/system-status`);
            return {
                success: true,
                response: `Estado del sistema Sheily AI:\n${JSON.stringify(response.data, null, 2)}`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error obteniendo estado: ${error.message}` };
        }
    }

    /**
     * Obtener información de ramas
     */
    async getBranchesInfo(branchName = null) {
        try {
            const url = branchName 
                ? `${this.advancedChatbotUrl}/api/chatbot/branches?branch=${branchName}`
                : `${this.advancedChatbotUrl}/api/chatbot/branches`;
            
            const response = await axios.get(url);
            return {
                success: true,
                response: `Información de ramas:\n${JSON.stringify(response.data, null, 2)}`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error obteniendo ramas: ${error.message}` };
        }
    }

    /**
     * Obtener información de módulos
     */
    async getModulesInfo() {
        try {
            const response = await axios.get(`${this.advancedChatbotUrl}/api/chatbot/modules`);
            return {
                success: true,
                response: `Módulos disponibles: ${response.data.total_modules} módulos cargados`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error obteniendo módulos: ${error.message}` };
        }
    }

    /**
     * Leer archivo
     */
    async readFile(filePath) {
        try {
            const response = await axios.post(`${this.advancedChatbotUrl}/api/chatbot/read-file`, {
                file_path: filePath,
                max_lines: 100
            });
            
            if (response.data.error) {
                return { error: response.data.error };
            }
            
            return {
                success: true,
                response: `Contenido del archivo ${filePath}:\n${response.data.content}`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error leyendo archivo: ${error.message}` };
        }
    }

    /**
     * Listar directorio
     */
    async listDirectory(dirPath) {
        try {
            const response = await axios.post(`${this.advancedChatbotUrl}/api/chatbot/list-dir`, {
                dir_path: dirPath
            });
            
            if (response.data.error) {
                return { error: response.data.error };
            }
            
            const items = response.data.items.map(item => 
                `${item.type === 'directory' ? '📁' : '📄'} ${item.name}`
            ).join('\n');
            
            return {
                success: true,
                response: `Contenido del directorio ${dirPath}:\n${items}`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error listando directorio: ${error.message}` };
        }
    }

    /**
     * Buscar en código
     */
    async searchInCode(query) {
        try {
            const response = await axios.post(`${this.advancedChatbotUrl}/api/chatbot/search`, {
                query: query,
                file_types: ['.py', '.js', '.json', '.md']
            });
            
            if (response.data.error) {
                return { error: response.data.error };
            }
            
            const results = response.data.results.map(result => 
                `📄 ${result.file} (${result.matches} coincidencias)`
            ).join('\n');
            
            return {
                success: true,
                response: `Resultados de búsqueda para "${query}":\n${results}`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error en búsqueda: ${error.message}` };
        }
    }

    /**
     * Ejecutar función de módulo
     */
    async executeModuleFunction(moduleName, functionName, args = []) {
        try {
            const response = await axios.post(`${this.advancedChatbotUrl}/api/chatbot/execute`, {
                module_name: moduleName,
                function_name: functionName,
                args: args
            });
            
            return {
                success: true,
                response: `Resultado de ${moduleName}.${functionName}:\n${response.data.result}`,
                data: response.data
            };
        } catch (error) {
            return { error: `Error ejecutando función: ${error.message}` };
        }
    }

    /**
     * Obtener ayuda
     */
    getHelp() {
        const helpText = `
🤖 COMANDOS DISPONIBLES EN SHEILY AI CHATBOT:

📊 INFORMACIÓN DEL SISTEMA:
  /status          - Estado completo del sistema
  /branches        - Lista todas las ramas
  /branches <rama> - Información de una rama específica
  /modules         - Lista todos los módulos disponibles

📁 EXPLORACIÓN DE ARCHIVOS:
  /read <archivo>  - Leer contenido de un archivo
  /list <dir>      - Listar contenido de un directorio
  /search <texto>  - Buscar texto en el código del proyecto

⚙️ EJECUCIÓN:
  /execute <módulo> <función> [args...] - Ejecutar función de un módulo

❓ AYUDA:
  /help            - Mostrar esta ayuda

💡 EJEMPLOS:
  /read backend/server.js
  /list modules
  /search "class DatabaseManager"
  /execute config.config_manager get_config
  /branches programación
        `;
        
        return {
            success: true,
            response: helpText
        };
    }

    /**
     * Verificar conectividad
     */
    async checkConnectivity() {
        const status = {
            advanced_chatbot: false,
            llm_server: false,
            timestamp: new Date().toISOString()
        };
        
        try {
            await axios.get(`${this.advancedChatbotUrl}/api/chatbot/system-status`, { timeout: 5000 });
            status.advanced_chatbot = true;
        } catch (e) {
            console.warn('⚠️ Chatbot avanzado no disponible');
        }
        
        try {
            await axios.get(`${this.llmServerUrl}/health`, { timeout: 5000 });
            status.llm_server = true;
        } catch (e) {
            console.warn('⚠️ Servidor LLM no disponible');
        }
        
        return status;
    }
}

module.exports = ChatbotIntegration;
