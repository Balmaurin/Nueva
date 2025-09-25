const WebSocket = require('ws');
const EventEmitter = require('events');

class ChatMetricsCollector extends EventEmitter {
  constructor() {
    super();
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      totalTokensUsed: 0,
      activeUsers: new Set(),
      requestsPerMinute: [],
      errorsPerMinute: [],
      modelStatus: 'unknown',
      uptime: Date.now(),
      lastRequest: null
    };
    
    this.wsClients = new Set();
    this.startMetricsCollection();
  }

  // Registrar una solicitud de chat
  recordRequest(userId, requestId, startTime) {
    this.metrics.totalRequests++;
    this.metrics.activeUsers.add(userId);
    this.metrics.lastRequest = new Date();
    
    // Agregar a requests por minuto
    const currentMinute = Math.floor(Date.now() / 60000);
    const minuteIndex = this.metrics.requestsPerMinute.findIndex(r => r.minute === currentMinute);
    
    if (minuteIndex >= 0) {
      this.metrics.requestsPerMinute[minuteIndex].count++;
    } else {
      this.metrics.requestsPerMinute.push({ minute: currentMinute, count: 1 });
      // Mantener solo las últimas 60 minutos
      if (this.metrics.requestsPerMinute.length > 60) {
        this.metrics.requestsPerMinute.shift();
      }
    }
    
    this.emit('request', { userId, requestId, startTime });
    this.broadcastMetrics();
  }

  // Registrar respuesta exitosa
  recordSuccess(userId, requestId, responseTime, tokensUsed) {
    this.metrics.successfulRequests++;
    this.metrics.totalTokensUsed += tokensUsed;
    
    // Calcular tiempo de respuesta promedio
    const currentAvg = this.metrics.averageResponseTime;
    const totalSuccess = this.metrics.successfulRequests;
    this.metrics.averageResponseTime = (currentAvg * (totalSuccess - 1) + responseTime) / totalSuccess;
    
    this.emit('success', { userId, requestId, responseTime, tokensUsed });
    this.broadcastMetrics();
  }

  // Registrar error
  recordError(userId, requestId, error, responseTime) {
    this.metrics.failedRequests++;
    
    // Agregar a errores por minuto
    const currentMinute = Math.floor(Date.now() / 60000);
    const minuteIndex = this.metrics.errorsPerMinute.findIndex(e => e.minute === currentMinute);
    
    if (minuteIndex >= 0) {
      this.metrics.errorsPerMinute[minuteIndex].count++;
      this.metrics.errorsPerMinute[minuteIndex].errors.push({
        type: error.name || 'Unknown',
        message: error.message || error.toString(),
        timestamp: new Date()
      });
    } else {
      this.metrics.errorsPerMinute.push({
        minute: currentMinute,
        count: 1,
        errors: [{
          type: error.name || 'Unknown',
          message: error.message || error.toString(),
          timestamp: new Date()
        }]
      });
      
      // Mantener solo las últimas 60 minutos
      if (this.metrics.errorsPerMinute.length > 60) {
        this.metrics.errorsPerMinute.shift();
      }
    }

    this.broadcastMetrics();
  }

  // Registrar solicitud de chat (compatible con el servidor)
  recordChatRequest(requestData) {
    this.metrics.totalRequests++;
    this.metrics.lastRequest = new Date();
    
    // Agregar a requests por minuto
    const currentMinute = Math.floor(Date.now() / 60000);
    const minuteIndex = this.metrics.requestsPerMinute.findIndex(r => r.minute === currentMinute);
    
    if (minuteIndex >= 0) {
      this.metrics.requestsPerMinute[minuteIndex].count++;
    } else {
      this.metrics.requestsPerMinute.push({ minute: currentMinute, count: 1 });
      // Mantener solo las últimas 60 minutos
      if (this.metrics.requestsPerMinute.length > 60) {
        this.metrics.requestsPerMinute.shift();
      }
    }
    
    this.emit('request', requestData);
    this.broadcastMetrics();
  }

  // Registrar respuesta de chat (compatible con el servidor)
  recordChatResponse(responseData) {
    if (responseData.success) {
      this.metrics.successfulRequests++;
      
      // Calcular tiempo de respuesta promedio
      const currentAvg = this.metrics.averageResponseTime;
      const totalSuccess = this.metrics.successfulRequests;
      this.metrics.averageResponseTime = (currentAvg * (totalSuccess - 1) + responseData.responseTime) / totalSuccess;
      
      this.emit('success', responseData);
    } else {
      this.metrics.failedRequests++;
      
      // Agregar a errores por minuto
      const currentMinute = Math.floor(Date.now() / 60000);
      const minuteIndex = this.metrics.errorsPerMinute.findIndex(e => e.minute === currentMinute);
      
      if (minuteIndex >= 0) {
        this.metrics.errorsPerMinute[minuteIndex].count++;
        this.metrics.errorsPerMinute[minuteIndex].errors.push({
          type: 'HTTP_ERROR',
          message: `HTTP ${responseData.statusCode}`,
          timestamp: new Date()
        });
      } else {
        this.metrics.errorsPerMinute.push({
          minute: currentMinute,
          count: 1,
          errors: [{
            type: 'HTTP_ERROR',
            message: `HTTP ${responseData.statusCode}`,
            timestamp: new Date()
          }]
        });
        
        // Mantener solo las últimas 60 minutos
        if (this.metrics.errorsPerMinute.length > 60) {
          this.metrics.errorsPerMinute.shift();
        }
      }
    }
    
    this.broadcastMetrics();
  }

  // Actualizar estado del modelo
  updateModelStatus(status) {
    this.metrics.modelStatus = status;
    this.emit('modelStatusChange', status);
    this.broadcastMetrics();
  }

  // Obtener métricas actuales
  getCurrentMetrics() {
    const now = Date.now();
    const uptime = now - this.metrics.uptime;
    
    return {
      ...this.metrics,
      uptime,
      uptimeFormatted: this.formatUptime(uptime),
      requestsPerMinute: this.metrics.requestsPerMinute.slice(-10), // Últimos 10 minutos
      errorsPerMinute: this.metrics.errorsPerMinute.slice(-10), // Últimos 10 minutos
      activeUsersCount: this.metrics.activeUsers.size,
      successRate: this.metrics.totalRequests > 0 ? 
        (this.metrics.successfulRequests / this.metrics.totalRequests * 100).toFixed(2) : 0,
      averageTokensPerRequest: this.metrics.successfulRequests > 0 ? 
        (this.metrics.totalTokensUsed / this.metrics.successfulRequests).toFixed(2) : 0
    };
  }

  // Formatear uptime
  formatUptime(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  // Iniciar recolección de métricas
  startMetricsCollection() {
    // Limpiar usuarios inactivos cada 5 minutos
    setInterval(() => {
      const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
      if (this.metrics.lastRequest && this.metrics.lastRequest.getTime() < fiveMinutesAgo) {
        this.metrics.activeUsers.clear();
        this.broadcastMetrics();
      }
    }, 5 * 60 * 1000);

    // Emitir métricas cada 10 segundos
    setInterval(() => {
      this.emit('metricsUpdate', this.getCurrentMetrics());
    }, 10000);
  }

  // Agregar cliente WebSocket
  addWebSocketClient(ws) {
    this.wsClients.add(ws);
    
    // Enviar métricas actuales inmediatamente
    ws.send(JSON.stringify({
      type: 'metrics',
      data: this.getCurrentMetrics()
    }));
    
    // Manejar desconexión
    ws.on('close', () => {
      this.wsClients.delete(ws);
    });
  }

  // Transmitir métricas a todos los clientes WebSocket
  broadcastMetrics() {
    const metrics = this.getCurrentMetrics();
    const message = JSON.stringify({
      type: 'metrics',
      data: metrics
    });
    
    this.wsClients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  // Obtener métricas para alertas
  getAlertMetrics() {
    const currentMetrics = this.getCurrentMetrics();
    const lastMinute = this.metrics.requestsPerMinute[this.metrics.requestsPerMinute.length - 1];
    const lastMinuteErrors = this.metrics.errorsPerMinute[this.metrics.errorsPerMinute.length - 1];
    
    return {
      currentRequestsPerMinute: lastMinute ? lastMinute.count : 0,
      currentErrorsPerMinute: lastMinuteErrors ? lastMinuteErrors.count : 0,
      successRate: currentMetrics.successRate,
      averageResponseTime: currentMetrics.averageResponseTime,
      modelStatus: currentMetrics.modelStatus,
      activeUsers: currentMetrics.activeUsersCount
    };
  }
}

module.exports = ChatMetricsCollector;
