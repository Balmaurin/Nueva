/**
 * Language Model Service - Sheily AI
 * Servicio para interactuar con el modelo Llama 3.2 3B Instruct Q8_0
 */

const axios = require('axios');

class LanguageModelService {
    constructor() {
        this.modelUrl = process.env.MODEL_SERVER_URL || 'http://localhost:8005';
        this.modelName = process.env.LLM_MODEL_NAME || 'Llama-3.2-3B-Instruct-Q8_0';
        this.timeout = parseInt(process.env.LLM_TIMEOUT || '60') * 1000;
        this.maxRetries = parseInt(process.env.LLM_MAX_RETRIES || '3');
        
        console.log(`🧠 Language Model Service inicializado:`);
        console.log(`   📍 URL: ${this.modelUrl}`);
        console.log(`   🤖 Modelo: ${this.modelName}`);
        console.log(`   ⏱️ Timeout: ${this.timeout}ms`);
    }

    /**
     * Generar respuesta usando el modelo LLM
     * @param {string} prompt - Prompt para el modelo
     * @param {Object} options - Opciones adicionales
     * @returns {Promise<string>} - Respuesta generada
     */
    async generateResponse(prompt, options = {}) {
        const {
            temperature = 0.7,
            max_tokens = 2048,
            system_prompt = "Eres Sheily AI, un asistente inteligente y útil. Responde de manera clara, precisa y amigable en español."
        } = options;

        const requestData = {
            model: this.modelName,
            messages: [
                {
                    role: "system",
                    content: system_prompt
                },
                {
                    role: "user", 
                    content: prompt
                }
            ],
            temperature: temperature,
            max_tokens: max_tokens,
            stream: false
        };

        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                console.log(`🔄 Enviando request al LLM (intento ${attempt}/${this.maxRetries})`);
                
                const response = await axios.post(`${this.modelUrl}/v1/chat/completions`, requestData, {
                    timeout: this.timeout,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.data && response.data.choices && response.data.choices[0]) {
                    const generatedText = response.data.choices[0].message.content;
                    console.log(`✅ Respuesta generada exitosamente (${generatedText.length} caracteres)`);
                    return generatedText;
                } else {
                    throw new Error('Formato de respuesta inválido del servidor LLM');
                }

            } catch (error) {
                console.error(`❌ Error en intento ${attempt}:`, error.message);

                if (attempt === this.maxRetries) {
                    throw new Error(`Servicio LLM no disponible: ${error.message}`);
                }

                await this.sleep(1000 * attempt);
            }
        }
    }

    /**
     * Verificar si el servicio LLM está disponible
     * @returns {Promise<boolean>} - True si está disponible
     */
    async isServiceAvailable() {
        try {
            const response = await axios.get(`${this.modelUrl}/health`, {
                timeout: 5000
            });
            return response.status === 200;
        } catch (error) {
            console.warn(`⚠️ Servicio LLM no disponible: ${error.message}`);
            return false;
        }
    }

    /**
     * Obtener información del modelo
     * @returns {Promise<Object>} - Información del modelo
     */
    async getModelInfo() {
        try {
            const response = await axios.get(`${this.modelUrl}/v1/models`, {
                timeout: 5000
            });
            return response.data;
        } catch (error) {
            console.warn(`⚠️ No se pudo obtener información del modelo: ${error.message}`);
            return {
                model: this.modelName,
                status: 'unknown',
                error: error.message
            };
        }
    }

    /**
     * Procesar chat con historial
     * @param {Array} messages - Historial de mensajes
     * @param {Object} options - Opciones adicionales
     * @returns {Promise<string>} - Respuesta generada
     */
    async processChat(messages, options = {}) {
        const {
            temperature = 0.7,
            max_tokens = 2048,
            system_prompt = "Eres Sheily AI, un asistente inteligente y útil. Responde de manera clara, precisa y amigable en español."
        } = options;

        // Preparar mensajes para el modelo
        const formattedMessages = [
            {
                role: "system",
                content: system_prompt
            },
            ...messages.map(msg => ({
                role: msg.role === 'user' ? 'user' : 'assistant',
                content: msg.content
            }))
        ];

        const requestData = {
            model: this.modelName,
            messages: formattedMessages,
            temperature: temperature,
            max_tokens: max_tokens,
            stream: false
        };

        try {
            const response = await axios.post(`${this.modelUrl}/v1/chat/completions`, requestData, {
                timeout: this.timeout,
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.data && response.data.choices && response.data.choices[0]) {
                return response.data.choices[0].message.content;
            } else {
                throw new Error('Formato de respuesta inválido del servidor LLM');
            }

        } catch (error) {
            console.error(`❌ Error procesando chat:`, error.message);
            throw new Error(`Servicio LLM no disponible: ${error.message}`);
        }
    }

    /**
     * Función helper para sleep
     * @param {number} ms - Milisegundos a esperar
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Obtener estadísticas del servicio
     * @returns {Object} - Estadísticas del servicio
     */
    getStats() {
        return {
            modelUrl: this.modelUrl,
            modelName: this.modelName,
            timeout: this.timeout,
            maxRetries: this.maxRetries,
            status: 'active'
        };
    }
}

module.exports = LanguageModelService;
