/**
 * Middleware de Validación de Entrada - Sheily AI
 * ===============================================
 * Middleware robusto para validación de entrada en todas las APIs
 */

const Joi = require('joi');

class ValidationMiddleware {
    constructor() {
        this.schemas = this.initializeSchemas();
    }

    initializeSchemas() {
        return {
            // Validación de autenticación
            register: Joi.object({
                username: Joi.string()
                    .alphanum()
                    .min(3)
                    .max(30)
                    .required()
                    .messages({
                        'string.alphanum': 'El nombre de usuario debe contener solo letras y números',
                        'string.min': 'El nombre de usuario debe tener al menos 3 caracteres',
                        'string.max': 'El nombre de usuario no puede tener más de 30 caracteres',
                        'any.required': 'El nombre de usuario es requerido'
                    }),
                email: Joi.string()
                    .email()
                    .required()
                    .messages({
                        'string.email': 'Debe proporcionar un email válido',
                        'any.required': 'El email es requerido'
                    }),
                password: Joi.string()
                    .min(12)
                    .max(128)
                    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
                    .required()
                    .messages({
                        'string.min': 'La contraseña debe tener al menos 12 caracteres',
                        'string.max': 'La contraseña no puede tener más de 128 caracteres',
                        'string.pattern.base': 'La contraseña debe contener al menos una letra minúscula, una mayúscula, un número y un carácter especial',
                        'any.required': 'La contraseña es requerida'
                    })
            }),

            login: Joi.object({
                username: Joi.string()
                    .required()
                    .messages({
                        'any.required': 'El nombre de usuario es requerido'
                    }),
                password: Joi.string()
                    .required()
                    .messages({
                        'any.required': 'La contraseña es requerida'
                    })
            }),

            // Validación de chat
            chatMessage: Joi.object({
                message: Joi.string()
                    .min(1)
                    .max(2000)
                    .required()
                    .messages({
                        'string.min': 'El mensaje no puede estar vacío',
                        'string.max': 'El mensaje no puede tener más de 2000 caracteres',
                        'any.required': 'El mensaje es requerido'
                    }),
                branch: Joi.string()
                    .optional()
                    .messages({
                        'string.base': 'La rama debe ser una cadena de texto'
                    }),
                session_id: Joi.string()
                    .uuid()
                    .optional()
                    .messages({
                        'string.guid': 'El session_id debe ser un UUID válido'
                    })
            }),

            // Validación de entrenamiento
            trainingStart: Joi.object({
                branch: Joi.string()
                    .required()
                    .messages({
                        'any.required': 'La rama es requerida'
                    }),
                level: Joi.number()
                    .integer()
                    .min(1)
                    .max(20)
                    .required()
                    .messages({
                        'number.base': 'El nivel debe ser un número',
                        'number.integer': 'El nivel debe ser un número entero',
                        'number.min': 'El nivel debe ser al menos 1',
                        'number.max': 'El nivel no puede ser mayor a 20',
                        'any.required': 'El nivel es requerido'
                    })
            }),

            trainingSubmit: Joi.object({
                exercise_id: Joi.number()
                    .integer()
                    .positive()
                    .required()
                    .messages({
                        'number.base': 'El ID del ejercicio debe ser un número',
                        'number.integer': 'El ID del ejercicio debe ser un número entero',
                        'number.positive': 'El ID del ejercicio debe ser positivo',
                        'any.required': 'El ID del ejercicio es requerido'
                    }),
                answer: Joi.string()
                    .min(1)
                    .max(500)
                    .required()
                    .messages({
                        'string.min': 'La respuesta no puede estar vacía',
                        'string.max': 'La respuesta no puede tener más de 500 caracteres',
                        'any.required': 'La respuesta es requerida'
                    }),
                session_id: Joi.string()
                    .uuid()
                    .required()
                    .messages({
                        'string.guid': 'El session_id debe ser un UUID válido',
                        'any.required': 'El session_id es requerido'
                    })
            }),

            // Validación de ramas
            branchQuery: Joi.object({
                branch: Joi.string()
                    .optional()
                    .messages({
                        'string.base': 'La rama debe ser una cadena de texto'
                    }),
                level: Joi.number()
                    .integer()
                    .min(1)
                    .max(20)
                    .optional()
                    .messages({
                        'number.base': 'El nivel debe ser un número',
                        'number.integer': 'El nivel debe ser un número entero',
                        'number.min': 'El nivel debe ser al menos 1',
                        'number.max': 'El nivel no puede ser mayor a 20'
                    }),
                type: Joi.string()
                    .valid('yes_no', 'true_false', 'multiple_choice')
                    .optional()
                    .messages({
                        'any.only': 'El tipo debe ser uno de: yes_no, true_false, multiple_choice'
                    })
            }),

            // Validación de prompts
            promptCreate: Joi.object({
                title: Joi.string()
                    .min(1)
                    .max(100)
                    .required()
                    .messages({
                        'string.min': 'El título no puede estar vacío',
                        'string.max': 'El título no puede tener más de 100 caracteres',
                        'any.required': 'El título es requerido'
                    }),
                content: Joi.string()
                    .min(1)
                    .max(5000)
                    .required()
                    .messages({
                        'string.min': 'El contenido no puede estar vacío',
                        'string.max': 'El contenido no puede tener más de 5000 caracteres',
                        'any.required': 'El contenido es requerido'
                    }),
                category: Joi.string()
                    .optional()
                    .messages({
                        'string.base': 'La categoría debe ser una cadena de texto'
                    })
            }),

            // Validación de caja fuerte
            vaultTransaction: Joi.object({
                amount: Joi.number()
                    .positive()
                    .precision(2)
                    .required()
                    .messages({
                        'number.base': 'El monto debe ser un número',
                        'number.positive': 'El monto debe ser positivo',
                        'number.precision': 'El monto no puede tener más de 2 decimales',
                        'any.required': 'El monto es requerido'
                    }),
                type: Joi.string()
                    .valid('deposit', 'withdraw', 'transfer')
                    .required()
                    .messages({
                        'any.only': 'El tipo debe ser uno de: deposit, withdraw, transfer',
                        'any.required': 'El tipo es requerido'
                    }),
                description: Joi.string()
                    .max(200)
                    .optional()
                    .messages({
                        'string.max': 'La descripción no puede tener más de 200 caracteres'
                    })
            }),

            // Validación de paginación
            pagination: Joi.object({
                page: Joi.number()
                    .integer()
                    .min(1)
                    .default(1)
                    .messages({
                        'number.base': 'La página debe ser un número',
                        'number.integer': 'La página debe ser un número entero',
                        'number.min': 'La página debe ser al menos 1'
                    }),
                limit: Joi.number()
                    .integer()
                    .min(1)
                    .max(100)
                    .default(10)
                    .messages({
                        'number.base': 'El límite debe ser un número',
                        'number.integer': 'El límite debe ser un número entero',
                        'number.min': 'El límite debe ser al menos 1',
                        'number.max': 'El límite no puede ser mayor a 100'
                    })
            })
        };
    }

    // Middleware genérico de validación
    validate(schemaName) {
        return (req, res, next) => {
            const schema = this.schemas[schemaName];
            
            if (!schema) {
                return res.status(500).json({
                    success: false,
                    error: 'Esquema de validación no encontrado',
                    details: `Esquema '${schemaName}' no existe`
                });
            }

            const { error, value } = schema.validate(req.body, {
                abortEarly: false,
                stripUnknown: true,
                convert: true
            });

            if (error) {
                const errorDetails = error.details.map(detail => ({
                    field: detail.path.join('.'),
                    message: detail.message,
                    value: detail.context?.value
                }));

                return res.status(400).json({
                    success: false,
                    error: 'Error de validación',
                    details: errorDetails
                });
            }

            // Reemplazar req.body con los datos validados y limpiados
            req.body = value;
            next();
        };
    }

    // Middleware para validar parámetros de URL
    validateParams(schemaName) {
        return (req, res, next) => {
            const schema = this.schemas[schemaName];
            
            if (!schema) {
                return res.status(500).json({
                    success: false,
                    error: 'Esquema de validación no encontrado'
                });
            }

            const { error, value } = schema.validate(req.params, {
                abortEarly: false,
                stripUnknown: true,
                convert: true
            });

            if (error) {
                const errorDetails = error.details.map(detail => ({
                    field: detail.path.join('.'),
                    message: detail.message,
                    value: detail.context?.value
                }));

                return res.status(400).json({
                    success: false,
                    error: 'Error de validación de parámetros',
                    details: errorDetails
                });
            }

            req.params = value;
            next();
        };
    }

    // Middleware para validar query parameters
    validateQuery(schemaName) {
        return (req, res, next) => {
            const schema = this.schemas[schemaName];
            
            if (!schema) {
                return res.status(500).json({
                    success: false,
                    error: 'Esquema de validación no encontrado'
                });
            }

            const { error, value } = schema.validate(req.query, {
                abortEarly: false,
                stripUnknown: true,
                convert: true
            });

            if (error) {
                const errorDetails = error.details.map(detail => ({
                    field: detail.path.join('.'),
                    message: detail.message,
                    value: detail.context?.value
                }));

                return res.status(400).json({
                    success: false,
                    error: 'Error de validación de query parameters',
                    details: errorDetails
                });
            }

            req.query = value;
            next();
        };
    }

    // Middleware para sanitizar entrada
    sanitizeInput(req, res, next) {
        // Sanitizar strings básicos
        const sanitizeString = (str) => {
            if (typeof str !== 'string') return str;
            
            return str
                .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remover scripts
                .replace(/<[^>]*>/g, '') // Remover HTML tags
                .replace(/javascript:/gi, '') // Remover javascript: URLs
                .replace(/on\w+\s*=/gi, '') // Remover event handlers
                .trim();
        };

        // Sanitizar objeto recursivamente
        const sanitizeObject = (obj) => {
            if (obj === null || obj === undefined) return obj;
            
            if (typeof obj === 'string') {
                return sanitizeString(obj);
            }
            
            if (Array.isArray(obj)) {
                return obj.map(sanitizeObject);
            }
            
            if (typeof obj === 'object') {
                const sanitized = {};
                for (const [key, value] of Object.entries(obj)) {
                    sanitized[key] = sanitizeObject(value);
                }
                return sanitized;
            }
            
            return obj;
        };

        // Sanitizar body, params y query
        if (req.body) {
            req.body = sanitizeObject(req.body);
        }
        
        if (req.params) {
            req.params = sanitizeObject(req.params);
        }
        
        if (req.query) {
            req.query = sanitizeObject(req.query);
        }

        next();
    }

    // Middleware para validar tamaño de payload
    validatePayloadSize(maxSize = 10 * 1024 * 1024) { // 10MB por defecto
        return (req, res, next) => {
            const contentLength = parseInt(req.get('content-length') || '0');
            
            if (contentLength > maxSize) {
                return res.status(413).json({
                    success: false,
                    error: 'Payload demasiado grande',
                    details: `El tamaño máximo permitido es ${maxSize / 1024 / 1024}MB`
                });
            }

            next();
        };
    }

    // Middleware para validar rate limiting personalizado
    validateRateLimit(maxRequests = 100, windowMs = 900000) { // 100 requests por 15 minutos
        const requests = new Map();

        return (req, res, next) => {
            const clientId = req.ip || req.connection.remoteAddress;
            const now = Date.now();
            const windowStart = now - windowMs;

            // Limpiar requests antiguos
            if (requests.has(clientId)) {
                const clientRequests = requests.get(clientId);
                const validRequests = clientRequests.filter(time => time > windowStart);
                requests.set(clientId, validRequests);
            } else {
                requests.set(clientId, []);
            }

            const clientRequests = requests.get(clientId);

            if (clientRequests.length >= maxRequests) {
                return res.status(429).json({
                    success: false,
                    error: 'Demasiadas solicitudes',
                    details: `Límite de ${maxRequests} solicitudes por ${windowMs / 1000 / 60} minutos excedido`,
                    retryAfter: Math.ceil(windowMs / 1000)
                });
            }

            // Agregar request actual
            clientRequests.push(now);
            requests.set(clientId, clientRequests);

            next();
        };
    }

    // Función para validar JWT token
    validateJWT(req, res, next) {
        const token = req.header('Authorization')?.replace('Bearer ', '');
        
        if (!token) {
            return res.status(401).json({
                success: false,
                error: 'Token de acceso requerido',
                details: 'Proporciona un token JWT válido en el header Authorization'
            });
        }

        try {
            const jwt = require('jsonwebtoken');
            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            req.user = decoded;
            next();
        } catch (error) {
            return res.status(401).json({
                success: false,
                error: 'Token inválido',
                details: error.message
            });
        }
    }

    // Función para validar roles
    validateRole(allowedRoles) {
        return (req, res, next) => {
            if (!req.user) {
                return res.status(401).json({
                    success: false,
                    error: 'Usuario no autenticado'
                });
            }

            if (!allowedRoles.includes(req.user.role)) {
                return res.status(403).json({
                    success: false,
                    error: 'Acceso denegado',
                    details: `Se requiere uno de los siguientes roles: ${allowedRoles.join(', ')}`
                });
            }

            next();
        };
    }
}

// Crear instancia singleton
const validationMiddleware = new ValidationMiddleware();

module.exports = validationMiddleware;
