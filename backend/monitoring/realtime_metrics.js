const WebSocket = require('ws');
const EventEmitter = require('events');
const os = require('os');

class RealtimeMetrics extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      port: config.port || 8004,
      updateInterval: config.updateInterval || 1000, // 1 segundo
      maxClients: config.maxClients || 100,
      enableSystemMetrics: config.enableSystemMetrics !== false,
      enableCustomMetrics: config.enableCustomMetrics !== false
    };
    
    this.wsServer = null;
    this.clients = new Set();
    this.metrics = {
      system: {},
      custom: {},
      performance: {},
      lastUpdate: Date.now()
    };
    
    this.customMetrics = new Map();
    this.performanceMetrics = new Map();
    
    this.startServer();
    this.startMetricsCollection();
  }
  
  // Iniciar servidor WebSocket
  startServer() {
    try {
      this.wsServer = new WebSocket.Server({ port: this.config.port });
      
      this.wsServer.on('connection', (ws, req) => {
        this.handleNewConnection(ws, req);
      });
      
      this.wsServer.on('error', (error) => {
        this.emit('error', error);
        console.error('❌ Error en servidor WebSocket de métricas:', error);
      });
      
      console.log(`🔌 Servidor WebSocket de métricas iniciado en puerto ${this.config.port}`);
    } catch (error) {
      console.error('❌ Error iniciando servidor de métricas:', error);
    }
  }
  
  // Manejar nueva conexión
  handleNewConnection(ws, req) {
    if (this.clients.size >= this.config.maxClients) {
      ws.close(1013, 'Límite de clientes alcanzado');
      return;
    }
    
    this.clients.add(ws);
    
    // Enviar métricas actuales inmediatamente
    ws.send(JSON.stringify({
      type: 'metrics',
      data: this.getCurrentMetrics()
    }));
    
    // Enviar historial de métricas
    ws.send(JSON.stringify({
      type: 'history',
      data: this.getMetricsHistory()
    }));
    
    ws.on('close', () => {
      this.clients.delete(ws);
    });
    
    ws.on('error', (error) => {
      console.error('Error en cliente WebSocket:', error);
      this.clients.delete(ws);
    });
    
    console.log(`📊 Cliente conectado a métricas en tiempo real. Total: ${this.clients.size}`);
  }
  
  // Iniciar recolección de métricas
  startMetricsCollection() {
    setInterval(() => {
      this.collectSystemMetrics();
      this.collectPerformanceMetrics();
      this.broadcastMetrics();
    }, this.config.updateInterval);
  }
  
  // Recolectar métricas del sistema
  collectSystemMetrics() {
    if (!this.config.enableSystemMetrics) return;
    
    try {
      const cpus = os.cpus();
      const totalMem = os.totalmem();
      const freeMem = os.freemem();
      const usedMem = totalMem - freeMem;
      
      this.metrics.system = {
        timestamp: Date.now(),
        cpu: {
          cores: cpus.length,
          model: cpus[0].model,
          speed: cpus[0].speed,
          load: os.loadavg(),
          usage: this.calculateCPUUsage(cpus)
        },
        memory: {
          total: totalMem,
          free: freeMem,
          used: usedMem,
          usagePercent: ((usedMem / totalMem) * 100).toFixed(2)
        },
        platform: {
          type: os.type(),
          release: os.release(),
          arch: os.arch(),
          uptime: os.uptime()
        },
        network: this.getNetworkStats()
      };
    } catch (error) {
      console.error('Error recolectando métricas del sistema:', error);
    }
  }
  
  // Calcular uso de CPU
  calculateCPUUsage(cpus) {
    try {
      const usage = cpus.map(cpu => {
        const total = Object.values(cpu.times).reduce((a, b) => a + b);
        const idle = cpu.times.idle;
        return ((total - idle) / total * 100).toFixed(2);
      });
      
      return {
        average: (usage.reduce((a, b) => parseFloat(a) + parseFloat(b), 0) / usage.length).toFixed(2),
        perCore: usage
      };
    } catch (error) {
      return { average: '0.00', perCore: [] };
    }
  }
  
  // Obtener estadísticas de red
  getNetworkStats() {
    try {
      const networkInterfaces = os.networkInterfaces();
      const stats = {};
      
      Object.keys(networkInterfaces).forEach(ifaceName => {
        const interfaces = networkInterfaces[ifaceName];
        interfaces.forEach(iface => {
          if (iface.family === 'IPv4' && !iface.internal) {
            stats[ifaceName] = {
              address: iface.address,
              netmask: iface.netmask,
              mac: iface.mac
            };
          }
        });
      });
      
      return stats;
    } catch (error) {
      return {};
    }
  }
  
  // Recolectar métricas de performance
  collectPerformanceMetrics() {
    if (!this.config.enableCustomMetrics) return;
    
    try {
      const memUsage = process.memoryUsage();
      
      this.metrics.performance = {
        timestamp: Date.now(),
        process: {
          pid: process.pid,
          memory: {
            rss: memUsage.rss,
            heapTotal: memUsage.heapTotal,
            heapUsed: memUsage.heapUsed,
            external: memUsage.external
          },
          cpu: process.cpuUsage(),
          uptime: process.uptime()
        },
        custom: Object.fromEntries(this.customMetrics),
        performance: Object.fromEntries(this.performanceMetrics)
      };
    } catch (error) {
      console.error('Error recolectando métricas de performance:', error);
    }
  }
  
  // Agregar métrica personalizada
  addCustomMetric(name, value, metadata = {}) {
    this.customMetrics.set(name, {
      value,
      metadata,
      timestamp: Date.now()
    });
    
    this.emit('customMetric', { name, value, metadata });
  }
  
  // Agregar métrica de performance
  addPerformanceMetric(name, value, unit = 'ms') {
    this.performanceMetrics.set(name, {
      value,
      unit,
      timestamp: Date.now()
    });
    
    this.emit('performanceMetric', { name, value, unit });
  }
  
  // Medir tiempo de operación
  startTimer(name) {
    const startTime = process.hrtime.bigint();
    
    return {
      stop: () => {
        const endTime = process.hrtime.bigint();
        const duration = Number(endTime - startTime) / 1000000; // Convertir a milisegundos
        
        this.addPerformanceMetric(name, duration, 'ms');
        return duration;
      }
    };
  }
  
  // Obtener métricas actuales
  getCurrentMetrics() {
    return {
      ...this.metrics,
      clients: this.clients.size,
      serverTime: Date.now()
    };
  }
  
  // Obtener historial de métricas
  getMetricsHistory() {
    // Implementar lógica para mantener historial de métricas
    return {
      system: this.metrics.system,
      performance: this.metrics.performance,
      lastUpdate: this.metrics.lastUpdate
    };
  }
  
  // Transmitir métricas a todos los clientes
  broadcastMetrics() {
    if (this.clients.size === 0) return;
    
    const metrics = this.getCurrentMetrics();
    const message = JSON.stringify({
      type: 'metrics',
      data: metrics,
      timestamp: Date.now()
    });
    
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(message);
        } catch (error) {
          console.error('Error enviando métricas a cliente:', error);
          this.clients.delete(client);
        }
      }
    });
    
    this.metrics.lastUpdate = Date.now();
    this.emit('metricsUpdate', metrics);
  }
  
  // Obtener estadísticas del servidor
  getServerStats() {
    return {
      port: this.config.port,
      clients: this.clients.size,
      maxClients: this.config.maxClients,
      uptime: process.uptime(),
      lastUpdate: this.metrics.lastUpdate,
      metrics: {
        system: this.config.enableSystemMetrics,
        custom: this.config.enableCustomMetrics
      }
    };
  }
  
  // Cambiar configuración dinámicamente
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    if (newConfig.updateInterval) {
      // Reiniciar intervalo si cambió
      clearInterval(this.metricsInterval);
      this.startMetricsCollection();
    }
    
    this.emit('configUpdate', this.config);
  }
  
  // Detener servidor
  stop() {
    if (this.wsServer) {
      this.wsServer.close();
    }
    
    this.clients.forEach(client => {
      client.close();
    });
    
    this.clients.clear();
    console.log('🛑 Servidor de métricas en tiempo real detenido');
  }
}

module.exports = RealtimeMetrics;
