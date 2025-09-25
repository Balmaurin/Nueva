const EventEmitter = require('events');

class SmartCache extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      maxSize: config.maxSize || 1000, // Máximo número de elementos
      maxMemory: config.maxMemory || 100 * 1024 * 1024, // 100MB
      defaultTTL: config.defaultTTL || 300000, // 5 minutos
      cleanupInterval: config.cleanupInterval || 60000, // 1 minuto
      enableStats: config.enableStats !== false,
      policy: config.policy || 'LRU' // LRU, LFU, FIFO
    };
    
    this.cache = new Map();
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      evictions: 0,
      size: 0,
      memoryUsage: 0
    };
    
    this.accessOrder = []; // Para LRU
    this.accessCount = new Map(); // Para LFU
    this.setupCleanup();
  }
  
  // Configurar limpieza automática
  setupCleanup() {
    setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }
  
  // Limpiar elementos expirados y excedidos
  cleanup() {
    const now = Date.now();
    let cleaned = 0;
    
    // Limpiar elementos expirados
    for (const [key, entry] of this.cache.entries()) {
      if (entry.expiresAt && entry.expiresAt < now) {
        this.delete(key);
        cleaned++;
      }
    }
    
    // Limpiar si excede el tamaño máximo
    if (this.cache.size > this.config.maxSize) {
      const toRemove = this.cache.size - this.config.maxSize;
      this.evictItems(toRemove);
      cleaned += toRemove;
    }
    
    // Limpiar si excede el límite de memoria
    if (this.stats.memoryUsage > this.config.maxMemory) {
      this.evictByMemory();
    }
    
    if (cleaned > 0) {
      this.emit('cleanup', { cleaned, remaining: this.cache.size });
    }
  }
  
  // Evadir elementos por política
  evictItems(count) {
    const keysToRemove = [];
    
    switch (this.config.policy) {
      case 'LRU':
        keysToRemove.push(...this.accessOrder.slice(0, count));
        break;
        
      case 'LFU':
        const sortedKeys = Array.from(this.accessCount.entries())
          .sort((a, b) => a[1] - b[1])
          .slice(0, count)
          .map(([key]) => key);
        keysToRemove.push(...sortedKeys);
        break;
        
      case 'FIFO':
        keysToRemove.push(...Array.from(this.cache.keys()).slice(0, count));
        break;
        
      default:
        keysToRemove.push(...Array.from(this.cache.keys()).slice(0, count));
    }
    
    keysToRemove.forEach(key => {
      if (this.cache.has(key)) {
        this.delete(key);
      }
    });
  }
  
  // Evadir por memoria
  evictByMemory() {
    const targetMemory = this.config.maxMemory * 0.8; // Reducir al 80%
    
    while (this.stats.memoryUsage > targetMemory && this.cache.size > 0) {
      let keyToRemove;
      
      switch (this.config.policy) {
        case 'LRU':
          keyToRemove = this.accessOrder[0];
          break;
          
        case 'LFU':
          const minKey = Array.from(this.accessCount.entries())
            .reduce((min, [key, count]) => count < min.count ? { key, count } : min, { count: Infinity });
          keyToRemove = minKey.key;
          break;
          
        default:
          keyToRemove = Array.from(this.cache.keys())[0];
      }
      
      if (keyToRemove) {
        this.delete(keyToRemove);
      }
    }
  }
  
  // Establecer elemento en cache
  set(key, value, options = {}) {
    const ttl = options.ttl || this.config.defaultTTL;
    const expiresAt = Date.now() + ttl;
    const size = this.estimateSize(value);
    
    // Verificar si hay espacio
    if (this.cache.size >= this.config.maxSize && !this.cache.has(key)) {
      this.evictItems(1);
    }
    
    // Verificar memoria
    if (this.stats.memoryUsage + size > this.config.maxMemory) {
      this.evictByMemory();
    }
    
    const entry = {
      value,
      expiresAt,
      size,
      createdAt: Date.now(),
      lastAccessed: Date.now(),
      accessCount: 0
    };
    
    // Actualizar orden de acceso para LRU
    this.updateAccessOrder(key);
    
    // Actualizar contador de acceso para LFU
    this.accessCount.set(key, 0);
    
    this.cache.set(key, entry);
    this.stats.sets++;
    this.stats.size = this.cache.size;
    this.stats.memoryUsage += size;
    
    this.emit('set', { key, value, size, ttl });
    
    return true;
  }
  
  // Obtener elemento del cache
  get(key) {
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.stats.misses++;
      this.emit('miss', { key });
      return null;
    }
    
    // Verificar expiración
    if (entry.expiresAt && entry.expiresAt < Date.now()) {
      this.delete(key);
      this.stats.misses++;
      this.emit('miss', { key, reason: 'expired' });
      return null;
    }
    
    // Actualizar estadísticas de acceso
    entry.lastAccessed = Date.now();
    entry.accessCount++;
    
    // Actualizar orden de acceso para LRU
    this.updateAccessOrder(key);
    
    // Actualizar contador de acceso para LFU
    this.accessCount.set(key, entry.accessCount);
    
    this.stats.hits++;
    this.emit('hit', { key, value: entry.value });
    
    return entry.value;
  }
  
  // Verificar si existe
  has(key) {
    const entry = this.cache.get(key);
    
    if (!entry) return false;
    
    if (entry.expiresAt && entry.expiresAt < Date.now()) {
      this.delete(key);
      return false;
    }
    
    return true;
  }
  
  // Eliminar elemento
  delete(key) {
    const entry = this.cache.get(key);
    
    if (entry) {
      this.stats.memoryUsage -= entry.size;
      this.stats.size = this.cache.size - 1;
      this.stats.deletes++;
      
      // Remover de orden de acceso
      const accessIndex = this.accessOrder.indexOf(key);
      if (accessIndex > -1) {
        this.accessOrder.splice(accessIndex, 1);
      }
      
      // Remover contador de acceso
      this.accessCount.delete(key);
      
      this.cache.delete(key);
      this.emit('delete', { key, size: entry.size });
    }
    
    return this.cache.has(key);
  }
  
  // Limpiar todo el cache
  clear() {
    const size = this.cache.size;
    const memoryUsage = this.stats.memoryUsage;
    
    this.cache.clear();
    this.accessOrder.length = 0;
    this.accessCount.clear();
    
    this.stats.size = 0;
    this.stats.memoryUsage = 0;
    
    this.emit('clear', { size, memoryUsage });
  }
  
  // Obtener estadísticas
  getStats() {
    if (!this.config.enableStats) return null;
    
    const hitRate = this.stats.hits + this.stats.misses > 0 
      ? (this.stats.hits / (this.stats.hits + this.stats.misses) * 100).toFixed(2)
      : 0;
    
    return {
      ...this.stats,
      hitRate: `${hitRate}%`,
      efficiency: this.calculateEfficiency(),
      policy: this.config.policy,
      config: {
        maxSize: this.config.maxSize,
        maxMemory: this.formatBytes(this.config.maxMemory),
        defaultTTL: this.config.defaultTTL,
        cleanupInterval: this.config.cleanupInterval
      }
    };
  }
  
  // Calcular eficiencia del cache
  calculateEfficiency() {
    const totalAccess = this.stats.hits + this.stats.misses;
    if (totalAccess === 0) return 0;
    
    const hitRate = this.stats.hits / totalAccess;
    const memoryEfficiency = 1 - (this.stats.memoryUsage / this.config.maxMemory);
    
    return ((hitRate * 0.7) + (memoryEfficiency * 0.3)).toFixed(3);
  }
  
  // Actualizar orden de acceso para LRU
  updateAccessOrder(key) {
    const index = this.accessOrder.indexOf(key);
    if (index > -1) {
      this.accessOrder.splice(index, 1);
    }
    this.accessOrder.push(key);
  }
  
  // Estimar tamaño del valor
  estimateSize(value) {
    try {
      const str = JSON.stringify(value);
      return Buffer.byteLength(str, 'utf8');
    } catch (error) {
      return 1024; // Tamaño por defecto si no se puede serializar
    }
  }
  
  // Formatear bytes
  formatBytes(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
  
  // Obtener claves
  keys() {
    return Array.from(this.cache.keys());
  }
  
  // Obtener valores
  values() {
    return Array.from(this.cache.values()).map(entry => entry.value);
  }
  
  // Obtener entradas
  entries() {
    return Array.from(this.cache.entries()).map(([key, entry]) => [key, entry.value]);
  }
  
  // Iterar sobre el cache
  forEach(callback) {
    this.cache.forEach((entry, key) => {
      callback(entry.value, key, entry);
    });
  }
  
  // Cambiar política de reemplazo
  setPolicy(policy) {
    if (['LRU', 'LFU', 'FIFO'].includes(policy)) {
      this.config.policy = policy;
      this.emit('policyChange', { policy });
    }
  }
  
  // Cambiar configuración
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    if (newConfig.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.setupCleanup();
    }
    
    this.emit('configUpdate', this.config);
  }
  
  // Obtener información del elemento
  getEntryInfo(key) {
    const entry = this.cache.get(key);
    
    if (!entry) return null;
    
    return {
      key,
      size: entry.size,
      createdAt: entry.createdAt,
      lastAccessed: entry.lastAccessed,
      accessCount: entry.accessCount,
      expiresAt: entry.expiresAt,
      isExpired: entry.expiresAt ? entry.expiresAt < Date.now() : false,
      ttl: entry.expiresAt ? Math.max(0, entry.expiresAt - Date.now()) : null
    };
  }
}

module.exports = SmartCache;
