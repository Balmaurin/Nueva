/**
 * Middleware de Configuración Unificada - Sheily AI
 * ================================================
 * Middleware para integrar el gestor de configuración unificado
 */

const { get_config, validate_config } = require('../../config/config_manager');

class ConfigMiddleware {
    constructor() {
        this.config = this.loadUnifiedConfig();
        this.validation = this.validateConfiguration();
    }

    loadUnifiedConfig() {
        try {
            return {
                server: {
                    port: get_config('server.port', 8000),
                    host: get_config('server.host', '127.0.0.1'),
                    cors_origins: get_config('server.cors_origins', ['http://localhost:3000'])
                },
                security: {
                    jwt: {
                        secret: get_config('security.jwt.secret'),
                        expiration: get_config('security.jwt.expiration', 3600),
                        algorithm: get_config('security.jwt.algorithm', 'HS256')
                    },
                    bcrypt: {
                        rounds: get_config('security.bcrypt.rounds', 12)
                    },
                    rate_limiting: {
                        window_ms: get_config('security.rate_limiting.window_ms', 900000),
                        max_requests: get_config('security.rate_limiting.max_requests', 100)
                    }
                },
                database: {
                    type: get_config('database.type', 'sqlite'),
                    host: get_config('database.host', 'localhost'),
                    port: get_config('database.port', 5432),
                    name: get_config('database.name', 'sheily_ai_db'),
                    user: get_config('database.user', 'sheily_ai_user')
                },
                ai_models: {
                    llm: {
                        server_url: get_config('ai_models.llm.server_url', 'http://localhost:8005'),
                        model_name: get_config('ai_models.llm.model_name', 'Llama-3.2-3B-Instruct-Q8_0'),
                        timeout: get_config('ai_models.llm.timeout', 60)
                    }
                },
                branches: {
                    total_branches: get_config('branches.total_branches', 35),
                    enabled: get_config('branches.enabled', true),
                    list: get_config('branches.list', [])
                },
                training: {
                    tokens_per_exercise: get_config('training.tokens_per_exercise', 10),
                    reward_multiplier: get_config('training.reward_multiplier', 1.5)
                }
            };
        } catch (error) {
            console.error('❌ Error cargando configuración unificada:', error);
            return this.getDefaultConfig();
        }
    }

    validateConfiguration() {
        try {
            const validation = validate_config();
            if (!validation.valid) {
                console.error('❌ Configuración inválida:', validation.errors);
                return { valid: false, errors: validation.errors };
            }
            return { valid: true, errors: [] };
        } catch (error) {
            console.error('❌ Error validando configuración:', error);
            return { valid: false, errors: [error.message] };
        }
    }

    getDefaultConfig() {
        return {
            server: { port: 8000, host: '127.0.0.1' },
            security: { jwt: { expiration: 3600 }, bcrypt: { rounds: 12 } },
            database: { type: 'sqlite', name: 'sheily_ai.db' },
            ai_models: { llm: { server_url: 'http://localhost:8005' } },
            branches: { total_branches: 35, enabled: true, list: [] },
            training: { tokens_per_exercise: 10, reward_multiplier: 1.5 }
        };
    }

    // Middleware para inyectar configuración en las requests
    injectConfig(req, res, next) {
        req.config = this.config;
        req.configValidation = this.validation;
        next();
    }

    // Middleware para validar configuración crítica
    validateCriticalConfig(req, res, next) {
        if (!this.validation.valid) {
            return res.status(500).json({
                error: 'Configuración del sistema inválida',
                details: this.validation.errors
            });
        }

        // Validar configuración crítica
        const criticalChecks = [
            { key: 'security.jwt.secret', message: 'JWT secret no configurado' },
            { key: 'branches.total_branches', message: 'Número de ramas no configurado' },
            { key: 'database.type', message: 'Tipo de base de datos no configurado' }
        ];

        for (const check of criticalChecks) {
            const value = get_config(check.key);
            if (!value) {
                return res.status(500).json({
                    error: 'Configuración crítica faltante',
                    details: check.message
                });
            }
        }

        next();
    }

    // Middleware para logging de configuración
    logConfig(req, res, next) {
        if (process.env.NODE_ENV === 'development') {
            console.log('🔧 Configuración cargada:');
            console.log(`   - Servidor: ${this.config.server.host}:${this.config.server.port}`);
            console.log(`   - Base de datos: ${this.config.database.type}`);
            console.log(`   - Ramas: ${this.config.branches.total_branches}`);
            console.log(`   - Modelo IA: ${this.config.ai_models.llm.model_name}`);
        }
        next();
    }

    // Obtener configuración para endpoints específicos
    getBranchesConfig() {
        return {
            total_branches: this.config.branches.total_branches,
            enabled: this.config.branches.enabled,
            list: this.config.branches.list
        };
    }

    getSecurityConfig() {
        return {
            jwt: this.config.security.jwt,
            bcrypt: this.config.security.bcrypt,
            rate_limiting: this.config.security.rate_limiting
        };
    }

    getDatabaseConfig() {
        return {
            type: this.config.database.type,
            host: this.config.database.host,
            port: this.config.database.port,
            name: this.config.database.name,
            user: this.config.database.user
        };
    }

    getAIConfig() {
        return {
            llm: this.config.ai_models.llm
        };
    }

    getTrainingConfig() {
        return {
            tokens_per_exercise: this.config.training.tokens_per_exercise,
            reward_multiplier: this.config.training.reward_multiplier
        };
    }

    // Endpoint para obtener configuración del sistema
    getSystemConfig(req, res) {
        try {
            const systemConfig = {
                system_name: get_config('system_name', 'Sheily AI'),
                version: get_config('version', '3.1.0'),
                environment: get_config('environment', 'development'),
                debug_mode: get_config('debug_mode', false),
                branches: this.getBranchesConfig(),
                database: this.getDatabaseConfig(),
                ai_models: this.getAIConfig(),
                training: this.getTrainingConfig(),
                validation: this.validation
            };

            res.json({
                success: true,
                config: systemConfig
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: 'Error obteniendo configuración del sistema',
                details: error.message
            });
        }
    }

    // Endpoint para validar configuración
    validateSystemConfig(req, res) {
        try {
            const validation = validate_config();
            
            res.json({
                success: true,
                validation: validation,
                config_status: validation.valid ? 'valid' : 'invalid'
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: 'Error validando configuración',
                details: error.message
            });
        }
    }
}

// Crear instancia singleton
const configMiddleware = new ConfigMiddleware();

module.exports = configMiddleware;
