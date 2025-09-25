/**
 * Sistema de Monitoreo Unificado - Sheily AI
 * ==========================================
 * Sistema completo de monitoreo y métricas del sistema
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class SystemMonitor {
    constructor() {
        this.metrics = {
            system: {},
            performance: {},
            security: {},
            database: {},
            api: {}
        };
        
        this.alerts = [];
        this.logFile = path.join(__dirname, '../../logs/system_monitor.log');
        this.ensureLogDirectory();
        
        // Inicializar métricas
        this.initializeMetrics();
        
        // Configurar monitoreo automático
        this.startMonitoring();
    }

    ensureLogDirectory() {
        const logDir = path.dirname(this.logFile);
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
    }

    initializeMetrics() {
        this.metrics = {
            system: {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                cpu: process.cpuUsage(),
                platform: os.platform(),
                arch: os.arch(),
                node_version: process.version,
                pid: process.pid
            },
            performance: {
                response_times: [],
                throughput: 0,
                error_rate: 0,
                active_connections: 0
            },
            security: {
                failed_logins: 0,
                blocked_requests: 0,
                suspicious_activities: 0,
                last_security_scan: new Date().toISOString()
            },
            database: {
                connection_status: 'unknown',
                query_count: 0,
                slow_queries: 0,
                connection_pool_size: 0
            },
            api: {
                total_requests: 0,
                successful_requests: 0,
                failed_requests: 0,
                endpoints: {}
            }
        };
    }

    startMonitoring() {
        // Monitoreo cada 30 segundos
        setInterval(() => {
            this.updateSystemMetrics();
            this.checkAlerts();
            this.logMetrics();
        }, 30000);

        // Limpieza de métricas cada 5 minutos
        setInterval(() => {
            this.cleanupMetrics();
        }, 300000);
    }

    updateSystemMetrics() {
        try {
            // Actualizar métricas del sistema
            this.metrics.system = {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                cpu: process.cpuUsage(),
                platform: os.platform(),
                arch: os.arch(),
                node_version: process.version,
                pid: process.pid,
                load_average: os.loadavg(),
                free_memory: os.freemem(),
                total_memory: os.totalmem()
            };

            // Calcular uso de memoria en porcentaje
            const memoryUsage = process.memoryUsage();
            const totalMemory = os.totalmem();
            this.metrics.system.memory_percentage = (memoryUsage.heapUsed / totalMemory) * 100;

            // Calcular uso de CPU
            const cpuUsage = process.cpuUsage();
            this.metrics.system.cpu_percentage = (cpuUsage.user + cpuUsage.system) / 1000000; // Convertir a segundos

        } catch (error) {
            this.logError('Error actualizando métricas del sistema', error);
        }
    }

    recordAPIRequest(endpoint, method, statusCode, responseTime) {
        try {
            this.metrics.api.total_requests++;
            
            if (statusCode >= 200 && statusCode < 300) {
                this.metrics.api.successful_requests++;
            } else {
                this.metrics.api.failed_requests++;
            }

            // Registrar tiempo de respuesta
            this.metrics.performance.response_times.push({
                timestamp: Date.now(),
                endpoint,
                method,
                statusCode,
                responseTime
            });

            // Mantener solo los últimos 1000 registros
            if (this.metrics.performance.response_times.length > 1000) {
                this.metrics.performance.response_times = this.metrics.performance.response_times.slice(-1000);
            }

            // Actualizar métricas por endpoint
            const endpointKey = `${method} ${endpoint}`;
            if (!this.metrics.api.endpoints[endpointKey]) {
                this.metrics.api.endpoints[endpointKey] = {
                    count: 0,
                    total_time: 0,
                    avg_time: 0,
                    errors: 0
                };
            }

            const endpointMetrics = this.metrics.api.endpoints[endpointKey];
            endpointMetrics.count++;
            endpointMetrics.total_time += responseTime;
            endpointMetrics.avg_time = endpointMetrics.total_time / endpointMetrics.count;

            if (statusCode >= 400) {
                endpointMetrics.errors++;
            }

        } catch (error) {
            this.logError('Error registrando request de API', error);
        }
    }

    recordDatabaseQuery(query, executionTime, success) {
        try {
            this.metrics.database.query_count++;
            
            if (!success) {
                this.metrics.database.slow_queries++;
            }

            // Registrar query lenta (>1 segundo)
            if (executionTime > 1000) {
                this.logWarning(`Query lenta detectada: ${query} (${executionTime}ms)`);
            }

        } catch (error) {
            this.logError('Error registrando query de base de datos', error);
        }
    }

    recordSecurityEvent(eventType, details) {
        try {
            switch (eventType) {
                case 'failed_login':
                    this.metrics.security.failed_logins++;
                    break;
                case 'blocked_request':
                    this.metrics.security.blocked_requests++;
                    break;
                case 'suspicious_activity':
                    this.metrics.security.suspicious_activities++;
                    break;
            }

            this.logSecurityEvent(eventType, details);

        } catch (error) {
            this.logError('Error registrando evento de seguridad', error);
        }
    }

    checkAlerts() {
        try {
            const alerts = [];

            // Alerta de uso de memoria alto
            if (this.metrics.system.memory_percentage > 80) {
                alerts.push({
                    type: 'memory_high',
                    severity: 'warning',
                    message: `Uso de memoria alto: ${this.metrics.system.memory_percentage.toFixed(2)}%`,
                    timestamp: new Date().toISOString()
                });
            }

            // Alerta de uso de CPU alto
            if (this.metrics.system.cpu_percentage > 80) {
                alerts.push({
                    type: 'cpu_high',
                    severity: 'warning',
                    message: `Uso de CPU alto: ${this.metrics.system.cpu_percentage.toFixed(2)}%`,
                    timestamp: new Date().toISOString()
                });
            }

            // Alerta de tasa de error alta
            const errorRate = this.metrics.api.total_requests > 0 ? 
                (this.metrics.api.failed_requests / this.metrics.api.total_requests) * 100 : 0;
            
            if (errorRate > 10) {
                alerts.push({
                    type: 'error_rate_high',
                    severity: 'critical',
                    message: `Tasa de error alta: ${errorRate.toFixed(2)}%`,
                    timestamp: new Date().toISOString()
                });
            }

            // Alerta de tiempo de respuesta alto
            const avgResponseTime = this.calculateAverageResponseTime();
            if (avgResponseTime > 3000) {
                alerts.push({
                    type: 'response_time_high',
                    severity: 'warning',
                    message: `Tiempo de respuesta alto: ${avgResponseTime.toFixed(2)}ms`,
                    timestamp: new Date().toISOString()
                });
            }

            // Alerta de intentos de login fallidos
            if (this.metrics.security.failed_logins > 10) {
                alerts.push({
                    type: 'failed_logins_high',
                    severity: 'warning',
                    message: `Muchos intentos de login fallidos: ${this.metrics.security.failed_logins}`,
                    timestamp: new Date().toISOString()
                });
            }

            // Procesar alertas
            alerts.forEach(alert => {
                this.processAlert(alert);
            });

        } catch (error) {
            this.logError('Error verificando alertas', error);
        }
    }

    processAlert(alert) {
        try {
            // Agregar a la lista de alertas
            this.alerts.push(alert);

            // Mantener solo las últimas 100 alertas
            if (this.alerts.length > 100) {
                this.alerts = this.alerts.slice(-100);
            }

            // Log de alerta
            this.logAlert(alert);

            // Enviar notificación si es crítica
            if (alert.severity === 'critical') {
                this.sendCriticalAlert(alert);
            }

        } catch (error) {
            this.logError('Error procesando alerta', error);
        }
    }

    calculateAverageResponseTime() {
        if (this.metrics.performance.response_times.length === 0) {
            return 0;
        }

        const recent = this.metrics.performance.response_times.slice(-100); // Últimos 100 requests
        const total = recent.reduce((sum, req) => sum + req.responseTime, 0);
        return total / recent.length;
    }

    cleanupMetrics() {
        try {
            // Limpiar métricas antiguas
            const oneHourAgo = Date.now() - (60 * 60 * 1000);
            
            this.metrics.performance.response_times = this.metrics.performance.response_times.filter(
                req => req.timestamp > oneHourAgo
            );

            // Limpiar alertas antiguas
            this.alerts = this.alerts.filter(
                alert => new Date(alert.timestamp) > new Date(oneHourAgo)
            );

        } catch (error) {
            this.logError('Error limpiando métricas', error);
        }
    }

    logMetrics() {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                metrics: {
                    system: {
                        uptime: this.metrics.system.uptime,
                        memory_percentage: this.metrics.system.memory_percentage,
                        cpu_percentage: this.metrics.system.cpu_percentage
                    },
                    api: {
                        total_requests: this.metrics.api.total_requests,
                        successful_requests: this.metrics.api.successful_requests,
                        failed_requests: this.metrics.api.failed_requests,
                        error_rate: this.metrics.api.total_requests > 0 ? 
                            (this.metrics.api.failed_requests / this.metrics.api.total_requests) * 100 : 0
                    },
                    performance: {
                        avg_response_time: this.calculateAverageResponseTime()
                    }
                }
            };

            const logLine = JSON.stringify(logEntry) + '\n';
            fs.appendFileSync(this.logFile, logLine);

        } catch (error) {
            console.error('Error escribiendo métricas al log:', error);
        }
    }

    logAlert(alert) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                type: 'alert',
                alert: alert
            };

            const logLine = JSON.stringify(logEntry) + '\n';
            fs.appendFileSync(this.logFile, logLine);

        } catch (error) {
            console.error('Error escribiendo alerta al log:', error);
        }
    }

    logSecurityEvent(eventType, details) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                type: 'security',
                event: eventType,
                details: details
            };

            const logLine = JSON.stringify(logEntry) + '\n';
            fs.appendFileSync(this.logFile, logLine);

        } catch (error) {
            console.error('Error escribiendo evento de seguridad al log:', error);
        }
    }

    logError(message, error) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                type: 'error',
                message: message,
                error: error.message,
                stack: error.stack
            };

            const logLine = JSON.stringify(logEntry) + '\n';
            fs.appendFileSync(this.logFile, logLine);

        } catch (logError) {
            console.error('Error escribiendo error al log:', logError);
        }
    }

    logWarning(message) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                type: 'warning',
                message: message
            };

            const logLine = JSON.stringify(logEntry) + '\n';
            fs.appendFileSync(this.logFile, logLine);

        } catch (error) {
            console.error('Error escribiendo warning al log:', error);
        }
    }

    sendCriticalAlert(alert) {
        // Implementar notificación de alerta crítica
        console.error(`🚨 ALERTA CRÍTICA: ${alert.message}`);
        
        // Aquí se podría implementar:
        // - Envío de email
        // - Notificación a Slack/Discord
        // - Webhook a sistema de monitoreo externo
    }

    getMetrics() {
        return {
            ...this.metrics,
            performance: {
                ...this.metrics.performance,
                avg_response_time: this.calculateAverageResponseTime(),
                error_rate: this.metrics.api.total_requests > 0 ? 
                    (this.metrics.api.failed_requests / this.metrics.api.total_requests) * 100 : 0
            }
        };
    }

    getAlerts() {
        return this.alerts;
    }

    getHealthStatus() {
        const errorRate = this.metrics.api.total_requests > 0 ? 
            (this.metrics.api.failed_requests / this.metrics.api.total_requests) * 100 : 0;
        
        const avgResponseTime = this.calculateAverageResponseTime();
        const memoryUsage = this.metrics.system.memory_percentage || 0;
        const cpuUsage = this.metrics.system.cpu_percentage || 0;

        let status = 'healthy';
        
        if (errorRate > 10 || avgResponseTime > 5000 || memoryUsage > 90 || cpuUsage > 90) {
            status = 'critical';
        } else if (errorRate > 5 || avgResponseTime > 3000 || memoryUsage > 80 || cpuUsage > 80) {
            status = 'warning';
        }

        return {
            status,
            timestamp: new Date().toISOString(),
            metrics: {
                error_rate: errorRate,
                avg_response_time: avgResponseTime,
                memory_usage: memoryUsage,
                cpu_usage: cpuUsage,
                uptime: this.metrics.system.uptime
            }
        };
    }
}

// Crear instancia singleton
const systemMonitor = new SystemMonitor();

module.exports = systemMonitor;
