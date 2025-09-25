const EventEmitter = require('events');
const nodemailer = require('nodemailer');

class ChatAlertSystem extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      email: {
        host: config.email?.host || 'smtp.gmail.com',
        port: config.email?.port || 587,
        secure: config.email?.secure || false,
        auth: {
          user: config.email?.user || process.env.ALERT_EMAIL_USER,
          pass: config.email?.pass || process.env.ALERT_EMAIL_PASS
        }
      },
      thresholds: {
        errorRate: config.thresholds?.errorRate || 10, // 10% de errores
        responseTime: config.thresholds?.responseTime || 5000, // 5 segundos
        requestsPerMinute: config.thresholds?.requestsPerMinute || 100,
        consecutiveErrors: config.thresholds?.consecutiveErrors || 5
      },
      notificationChannels: config.notificationChannels || ['email', 'console']
    };
    
    this.alerts = [];
    this.consecutiveErrors = 0;
    this.lastAlertTime = {};
    this.alertCooldown = 5 * 60 * 1000; // 5 minutos entre alertas del mismo tipo
    
    this.setupEmailTransporter();
  }

  // Configurar transportador de email
  setupEmailTransporter() {
    if (this.config.email.auth.user && this.config.email.auth.pass && this.config.email.auth.user.trim() !== '') {
      try {
        this.emailTransporter = nodemailer.createTransport(this.config.email);
        console.log('✅ Transportador de email configurado para alertas');
      } catch (error) {
        console.warn('⚠️ Error configurando email para alertas:', error.message);
        this.emailTransporter = null;
      }
    } else {
      console.log('ℹ️ Configuración de email no disponible - alertas solo en consola');
      this.emailTransporter = null;
    }
  }

  // Procesar métricas y generar alertas
  processMetrics(metrics) {
    const alerts = [];
    
    // Log de depuración para entender las métricas
    console.log(`🔍 Debug - Métricas recibidas:`, {
      successRate: metrics.successRate,
      errorRate: 100 - metrics.successRate,
      threshold: this.config.thresholds.errorRate,
      minSuccessRate: 100 - this.config.thresholds.errorRate
    });
    
    // Verificar tasa de errores - CORREGIDO: solo alertar cuando successRate sea menor al umbral mínimo
    const minSuccessRate = 100 - this.config.thresholds.errorRate;
    if (metrics.successRate < minSuccessRate) {
      alerts.push({
        type: 'HIGH_ERROR_RATE',
        severity: 'HIGH',
        message: `Tasa de errores alta: ${(100 - metrics.successRate).toFixed(2)}% (umbral: ${this.config.thresholds.errorRate}%)`,
        metrics: metrics,
        timestamp: new Date()
      });
    }
    
    // Verificar tiempo de respuesta
    if (metrics.averageResponseTime > this.config.thresholds.responseTime) {
      alerts.push({
        type: 'HIGH_RESPONSE_TIME',
        severity: 'MEDIUM',
        message: `Tiempo de respuesta alto: ${metrics.averageResponseTime}ms (umbral: ${this.config.thresholds.responseTime}ms)`,
        metrics: metrics,
        timestamp: new Date()
      });
    }
    
    // Verificar requests por minuto
    if (metrics.currentRequestsPerMinute > this.config.thresholds.requestsPerMinute) {
      alerts.push({
        type: 'HIGH_TRAFFIC',
        severity: 'MEDIUM',
        message: `Tráfico alto: ${metrics.currentRequestsPerMinute} requests/min (umbral: ${this.config.thresholds.requestsPerMinute})`,
        metrics: metrics,
        timestamp: new Date()
      });
    }
    
    // Verificar estado del modelo
    if (metrics.modelStatus === 'unavailable') {
      alerts.push({
        type: 'MODEL_UNAVAILABLE',
        severity: 'CRITICAL',
        message: 'Modelo de lenguaje no disponible',
        metrics: metrics,
        timestamp: new Date()
      });
    }
    
    // Verificar errores consecutivos
    if (metrics.currentErrorsPerMinute > 0) {
      this.consecutiveErrors++;
      if (this.consecutiveErrors >= this.config.thresholds.consecutiveErrors) {
        alerts.push({
          type: 'CONSECUTIVE_ERRORS',
          severity: 'HIGH',
          message: `${this.consecutiveErrors} errores consecutivos detectados`,
          metrics: metrics,
          timestamp: new Date()
        });
      }
    } else {
      this.consecutiveErrors = 0;
    }
    
    // Procesar alertas
    alerts.forEach(alert => this.processAlert(alert));
  }

  // Procesar una alerta individual
  processAlert(alert) {
    // Verificar cooldown para evitar spam de alertas
    const alertKey = alert.type;
    const now = Date.now();
    
    if (this.lastAlertTime[alertKey] && 
        (now - this.lastAlertTime[alertKey]) < this.alertCooldown) {
      return; // Aún en cooldown
    }
    
    // Actualizar tiempo de última alerta
    this.lastAlertTime[alertKey] = now;
    
    // Agregar a historial de alertas
    this.alerts.push(alert);
    
    // Mantener solo las últimas 100 alertas
    if (this.alerts.length > 100) {
      this.alerts.shift();
    }
    
    // Emitir evento de alerta
    this.emit('alert', alert);
    
    // Enviar notificaciones
    this.sendNotifications(alert);
    
    // Log de la alerta
    console.error(`🚨 ALERTA [${alert.severity}]: ${alert.message}`);
  }

  // Enviar notificaciones por diferentes canales
  async sendNotifications(alert) {
    for (const channel of this.config.notificationChannels) {
      try {
        switch (channel) {
          case 'email':
            await this.sendEmailAlert(alert);
            break;
          case 'console':
            this.sendConsoleAlert(alert);
            break;
          case 'webhook':
            await this.sendWebhookAlert(alert);
            break;
        }
      } catch (error) {
        console.error(`Error enviando alerta por ${channel}:`, error);
      }
    }
  }

  // Enviar alerta por email
  async sendEmailAlert(alert) {
    if (!this.emailTransporter) {
      console.log('ℹ️ Transportador de email no configurado - alerta solo en consola');
      return;
    }
    
    try {
      const mailOptions = {
        from: this.config.email.auth.user,
        to: process.env.ALERT_EMAIL_TO || this.config.email.auth.user,
        subject: `🚨 Alerta Chat 4-bit: ${alert.type}`,
        html: this.generateEmailAlertHTML(alert)
      };
      
      await this.emailTransporter.sendMail(mailOptions);
      console.log(`📧 Alerta enviada por email: ${alert.type}`);
    } catch (error) {
      console.error('❌ Error enviando alerta por email:', error.message);
      // Fallback a consola si falla el email
      this.sendConsoleAlert(alert);
    }
  }

  // Generar HTML para alerta por email
  generateEmailAlertHTML(alert) {
    return `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #d32f2f;">🚨 Alerta del Sistema Chat 4-bit</h2>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
          <h3 style="margin: 0 0 10px 0; color: #333;">${alert.message}</h3>
          
          <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Tipo:</td>
              <td style="padding: 8px; border: 1px solid #ddd;">${alert.type}</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Severidad:</td>
              <td style="padding: 8px; border: 1px solid #ddd;">${alert.severity}</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Timestamp:</td>
              <td style="padding: 8px; border: 1px solid #ddd;">${alert.timestamp.toLocaleString()}</td>
            </tr>
          </table>
        </div>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px;">
          <h4 style="margin: 0 0 10px 0; color: #1976d2;">Métricas Actuales:</h4>
          <ul style="margin: 0; padding-left: 20px;">
            <li>Tasa de éxito: ${alert.metrics.successRate}%</li>
            <li>Tiempo de respuesta promedio: ${alert.metrics.averageResponseTime}ms</li>
            <li>Requests por minuto: ${alert.metrics.currentRequestsPerMinute}</li>
            <li>Errores por minuto: ${alert.metrics.currentErrorsPerMinute}</li>
            <li>Estado del modelo: ${alert.metrics.modelStatus}</li>
            <li>Usuarios activos: ${alert.metrics.activeUsers}</li>
          </ul>
        </div>
        
        <p style="color: #666; font-size: 12px; margin-top: 20px;">
          Esta alerta fue generada automáticamente por el sistema de monitoreo de Sheily AI.
        </p>
      </div>
    `;
  }

  // Enviar alerta por consola
  sendConsoleAlert(alert) {
    const colors = {
      CRITICAL: '\x1b[31m', // Rojo
      HIGH: '\x1b[33m',     // Amarillo
      MEDIUM: '\x1b[36m',   // Cyan
      LOW: '\x1b[32m'       // Verde
    };
    
    const reset = '\x1b[0m';
    const color = colors[alert.severity] || colors.MEDIUM;
    
    console.log(`${color}🚨 ALERTA [${alert.severity}]${reset}`);
    console.log(`${color}${alert.message}${reset}`);
    console.log(`${color}Timestamp: ${alert.timestamp.toLocaleString()}${reset}`);
    console.log(`${color}Tipo: ${alert.type}${reset}`);
    console.log('---');
  }

  // Enviar alerta por webhook (para integración con Slack, Discord, etc.)
  async sendWebhookAlert(alert) {
    const webhookUrl = process.env.ALERT_WEBHOOK_URL;
    if (!webhookUrl) return;
    
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: `🚨 *Alerta Chat 4-bit [${alert.severity}]*\n${alert.message}`,
          attachments: [{
            fields: [
              { title: 'Tipo', value: alert.type, short: true },
              { title: 'Severidad', value: alert.severity, short: true },
              { title: 'Tasa de Éxito', value: `${alert.metrics.successRate}%`, short: true },
              { title: 'Estado del Modelo', value: alert.metrics.modelStatus, short: true }
            ],
            color: this.getSeverityColor(alert.severity)
          }]
        })
      });
      
      if (response.ok) {
        console.log(`🔗 Alerta enviada por webhook: ${alert.type}`);
      }
    } catch (error) {
      console.error('Error enviando webhook:', error);
    }
  }

  // Obtener color para la severidad
  getSeverityColor(severity) {
    const colors = {
      CRITICAL: '#d32f2f',
      HIGH: '#f57c00',
      MEDIUM: '#1976d2',
      LOW: '#388e3c'
    };
    return colors[severity] || colors.MEDIUM;
  }

  // Obtener historial de alertas
  getAlertHistory(limit = 50) {
    return this.alerts.slice(-limit);
  }

  // Obtener estadísticas de alertas
  getAlertStats() {
    const now = Date.now();
    const last24h = now - 24 * 60 * 60 * 1000;
    const lastHour = now - 60 * 60 * 1000;
    
    const alerts24h = this.alerts.filter(a => a.timestamp.getTime() > last24h);
    const alerts1h = this.alerts.filter(a => a.timestamp.getTime() > lastHour);
    
    const severityCounts = this.alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
      return acc;
    }, {});
    
    return {
      total: this.alerts.length,
      last24h: alerts24h.length,
      lastHour: alerts1h.length,
      bySeverity: severityCounts,
      lastAlert: this.alerts.length > 0 ? this.alerts[this.alerts.length - 1] : null
    };
  }

  // Limpiar alertas antiguas
  cleanupOldAlerts(maxAge = 7 * 24 * 60 * 60 * 1000) { // 7 días
    const cutoff = Date.now() - maxAge;
    this.alerts = this.alerts.filter(alert => alert.timestamp.getTime() > cutoff);
  }
}

module.exports = ChatAlertSystem;
