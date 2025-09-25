const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

class AdvancedLogger extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      logDir: config.logDir || './logs',
      maxFileSize: config.maxFileSize || 10 * 1024 * 1024, // 10MB
      maxFiles: config.maxFiles || 5,
      logLevel: config.logLevel || 'info',
      enableConsole: config.enableConsole !== false,
      enableFile: config.enableFile !== false,
      format: config.format || 'json', // 'json' o 'text'
      timestampFormat: config.timestampFormat || 'ISO'
    };
    
    this.logLevels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3,
      trace: 4
    };
    
    this.currentLevel = this.logLevels[this.config.logLevel] || 2;
    
    this.ensureLogDirectory();
    this.setupLogRotation();
  }
  
  // Crear directorio de logs si no existe
  ensureLogDirectory() {
    if (!fs.existsSync(this.config.logDir)) {
      fs.mkdirSync(this.config.logDir, { recursive: true });
    }
  }
  
  // Configurar rotación automática de logs
  setupLogRotation() {
    setInterval(() => {
      this.rotateLogs();
    }, 60 * 1000); // Verificar cada minuto
  }
  
  // Rotar logs cuando excedan el tamaño máximo
  rotateLogs() {
    const logFile = path.join(this.config.logDir, 'application.log');
    
    if (fs.existsSync(logFile)) {
      const stats = fs.statSync(logFile);
      
      if (stats.size > this.config.maxFileSize) {
        this.rotateLogFile(logFile);
      }
    }
  }
  
  // Rotar archivo de log
  rotateLogFile(logFile) {
    try {
      // Crear backup con timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupFile = path.join(this.config.logDir, `application-${timestamp}.log`);
      
      fs.renameSync(logFile, backupFile);
      
      // Limpiar archivos antiguos
      this.cleanOldLogs();
      
      console.log(`📁 Log rotado: ${backupFile}`);
    } catch (error) {
      console.error('Error rotando logs:', error);
    }
  }
  
  // Limpiar logs antiguos
  cleanOldLogs() {
    try {
      const files = fs.readdirSync(this.config.logDir);
      const logFiles = files
        .filter(file => file.startsWith('application-') && file.endsWith('.log'))
        .map(file => ({
          name: file,
          path: path.join(this.config.logDir, file),
          time: fs.statSync(path.join(this.config.logDir, file)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time);
      
      // Mantener solo los archivos más recientes
      if (logFiles.length > this.config.maxFiles) {
        const filesToDelete = logFiles.slice(this.config.maxFiles);
        
        filesToDelete.forEach(file => {
          fs.unlinkSync(file.path);
          console.log(`🗑️ Log eliminado: ${file.name}`);
        });
      }
    } catch (error) {
      console.error('Error limpiando logs antiguos:', error);
    }
  }
  
  // Generar timestamp
  getTimestamp() {
    if (this.config.timestampFormat === 'ISO') {
      return new Date().toISOString();
    } else {
      return new Date().toLocaleString('es-ES');
    }
  }
  
  // Formatear mensaje de log
  formatMessage(level, message, meta = {}) {
    const logEntry = {
      timestamp: this.getTimestamp(),
      level: level.toUpperCase(),
      message,
      ...meta
    };
    
    if (this.config.format === 'json') {
      return JSON.stringify(logEntry);
    } else {
      return `[${logEntry.timestamp}] [${logEntry.level}] ${logEntry.message}`;
    }
  }
  
  // Escribir en archivo
  writeToFile(message) {
    if (!this.config.enableFile) return;
    
    try {
      const logFile = path.join(this.config.logDir, 'application.log');
      fs.appendFileSync(logFile, message + '\n');
    } catch (error) {
      console.error('Error escribiendo en archivo de log:', error);
    }
  }
  
  // Escribir en consola
  writeToConsole(message, level) {
    if (!this.config.enableConsole) return;
    
    const colors = {
      error: '\x1b[31m', // Rojo
      warn: '\x1b[33m',  // Amarillo
      info: '\x1b[36m',  // Cyan
      debug: '\x1b[32m', // Verde
      trace: '\x1b[35m'  // Magenta
    };
    
    const reset = '\x1b[0m';
    const color = colors[level] || colors.info;
    
    console.log(`${color}${message}${reset}`);
  }
  
  // Método principal de logging
  log(level, message, meta = {}) {
    if (this.logLevels[level] > this.currentLevel) {
      return;
    }
    
    const formattedMessage = this.formatMessage(level, message, meta);
    
    this.writeToFile(formattedMessage);
    this.writeToConsole(formattedMessage, level);
    
    // Emitir evento para otros sistemas
    this.emit('log', { level, message, meta, timestamp: this.getTimestamp() });
    
    // Emitir eventos específicos por nivel
    this.emit(level, { message, meta, timestamp: this.getTimestamp() });
  }
  
  // Métodos de conveniencia
  error(message, meta = {}) {
    this.log('error', message, meta);
  }
  
  warn(message, meta = {}) {
    this.log('warn', message, meta);
  }
  
  info(message, meta = {}) {
    this.log('info', message, meta);
  }
  
  debug(message, meta = {}) {
    this.log('debug', message, meta);
  }
  
  trace(message, meta = {}) {
    this.log('trace', message, meta);
  }
  
  // Log de performance
  time(label) {
    console.time(label);
    return label;
  }
  
  timeEnd(label) {
    console.timeEnd(label);
  }
  
  // Log de métricas
  metric(name, value, unit = '') {
    this.info(`📊 Métrica: ${name} = ${value}${unit}`, { type: 'metric', name, value, unit });
  }
  
  // Log de eventos del sistema
  systemEvent(event, details = {}) {
    this.info(`🔧 Evento del sistema: ${event}`, { type: 'system_event', event, details });
  }
  
  // Log de errores con stack trace
  errorWithStack(message, error, meta = {}) {
    this.error(message, {
      ...meta,
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      }
    });
  }
  
  // Obtener estadísticas de logs
  getLogStats() {
    try {
      const logFile = path.join(this.config.logDir, 'application.log');
      
      if (!fs.existsSync(logFile)) {
        return { size: 0, lines: 0, lastModified: null };
      }
      
      const stats = fs.statSync(logFile);
      const content = fs.readFileSync(logFile, 'utf8');
      const lines = content.split('\n').filter(line => line.trim()).length;
      
      return {
        size: stats.size,
        lines,
        lastModified: stats.mtime,
        logLevel: this.config.logLevel,
        maxFileSize: this.config.maxFileSize,
        maxFiles: this.config.maxFiles
      };
    } catch (error) {
      return { error: error.message };
    }
  }
  
  // Cambiar nivel de log dinámicamente
  setLogLevel(level) {
    if (this.logLevels.hasOwnProperty(level)) {
      this.currentLevel = this.logLevels[level];
      this.config.logLevel = level;
      this.info(`Nivel de log cambiado a: ${level}`);
    } else {
      this.warn(`Nivel de log inválido: ${level}`);
    }
  }
}

module.exports = AdvancedLogger;
