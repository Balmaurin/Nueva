const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const archiver = require('archiver');

class ChatBackupSystem {
  constructor(config = {}) {
    this.config = {
      backupDir: config.backupDir || './backups/chat',
      maxBackups: config.maxBackups || 10,
      backupInterval: config.backupInterval || 24 * 60 * 60 * 1000, // 24 horas
      compressionLevel: config.compressionLevel || 9,
      includeMetadata: config.includeMetadata !== false,
      retentionDays: config.retentionDays || 30
    };
    
    this.db = null;
    this.backupInProgress = false;
    this.lastBackupTime = null;
    this.backupStats = {
      totalBackups: 0,
      successfulBackups: 0,
      failedBackups: 0,
      lastBackupSize: 0,
      totalBackupSize: 0
    };
    
    this.ensureBackupDirectory();
    this.startScheduledBackups();
  }

  // Establecer conexión a la base de datos
  setDatabase(db) {
    this.db = db;
  }

  // Asegurar que el directorio de backup existe
  async ensureBackupDirectory() {
    try {
      await fs.mkdir(this.config.backupDir, { recursive: true });
      console.log(`✅ Directorio de backup creado: ${this.config.backupDir}`);
    } catch (error) {
      console.error('❌ Error creando directorio de backup:', error);
    }
  }

  // Iniciar backups programados
  startScheduledBackups() {
    setInterval(async () => {
      if (!this.backupInProgress) {
        await this.createBackup();
      }
    }, this.config.backupInterval);
    
    console.log(`🔄 Backup automático programado cada ${this.config.backupInterval / (60 * 60 * 1000)} horas`);
  }

  // Crear backup completo
  async createBackup() {
    if (this.backupInProgress) {
      console.log('⚠️ Backup ya en progreso, saltando...');
      return;
    }

    this.backupInProgress = true;
    const backupId = uuidv4();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupName = `chat_backup_${timestamp}_${backupId}`;
    const backupPath = path.join(this.config.backupDir, backupName);
    
    try {
      console.log(`🔄 Iniciando backup: ${backupName}`);
      
      // Crear directorio temporal para el backup
      const tempDir = path.join(this.config.backupDir, 'temp', backupName);
      await fs.mkdir(tempDir, { recursive: true });
      
      // Exportar datos de la base de datos
      await this.exportDatabaseData(tempDir);
      
      // Crear archivo de metadatos
      if (this.config.includeMetadata) {
        await this.createMetadataFile(tempDir, backupId, timestamp);
      }
      
      // Comprimir backup
      const archivePath = await this.compressBackup(tempDir, backupPath);
      
      // Limpiar directorio temporal
      await fs.rm(tempDir, { recursive: true, force: true });
      
      // Verificar integridad del backup
      const backupSize = await this.verifyBackup(archivePath);
      
      // Actualizar estadísticas
      this.updateBackupStats(true, backupSize);
      this.lastBackupTime = new Date();
      
      // Limpiar backups antiguos
      await this.cleanupOldBackups();
      
      console.log(`✅ Backup completado exitosamente: ${backupName} (${this.formatBytes(backupSize)})`);
      
    } catch (error) {
      console.error(`❌ Error en backup ${backupName}:`, error);
      this.updateBackupStats(false, 0);
      
      // Limpiar archivos parciales
      try {
        await fs.rm(backupPath, { force: true });
        const tempDir = path.join(this.config.backupDir, 'temp', backupName);
        await fs.rm(tempDir, { recursive: true, force: true });
      } catch (cleanupError) {
        console.error('Error limpiando archivos parciales:', cleanupError);
      }
    } finally {
      this.backupInProgress = false;
    }
  }

  // Exportar datos de la base de datos
  async exportDatabaseData(backupDir) {
    if (!this.db) {
      throw new Error('Base de datos no configurada');
    }
    
    console.log('📊 Exportando datos de la base de datos...');
    
    // Exportar conversaciones
    const conversations = await this.db.any(`
      SELECT 
        cm.*,
        cs.created_at as session_created,
        u.username
      FROM chat_messages cm
      JOIN chat_sessions cs ON cm.session_id = cs.session_id
      JOIN users u ON cm.user_id = u.id
      ORDER BY cm.timestamp ASC
    `);
    
    await fs.writeFile(
      path.join(backupDir, 'conversations.json'),
      JSON.stringify(conversations, null, 2)
    );
    
    // Exportar sesiones de chat
    const sessions = await this.db.any(`
      SELECT * FROM chat_sessions ORDER BY created_at ASC
    `);
    
    await fs.writeFile(
      path.join(backupDir, 'sessions.json'),
      JSON.stringify(sessions, null, 2)
    );
    
    // Exportar usuarios
    const users = await this.db.any(`
      SELECT id, username, email, created_at FROM users ORDER BY created_at ASC
    `);
    
    await fs.writeFile(
      path.join(backupDir, 'users.json'),
      JSON.stringify(users, null, 2)
    );
    
    // Exportar estadísticas
    const stats = await this.db.one(`
      SELECT 
        COUNT(*) as total_messages,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT session_id) as total_sessions,
        MIN(timestamp) as first_message,
        MAX(timestamp) as last_message
      FROM chat_messages
    `);
    
    await fs.writeFile(
      path.join(backupDir, 'statistics.json'),
      JSON.stringify(stats, null, 2)
    );
    
    console.log(`📊 Exportados ${conversations.length} mensajes, ${sessions.length} sesiones, ${users.length} usuarios`);
  }

  // Crear archivo de metadatos
  async createMetadataFile(backupDir, backupId, timestamp) {
    const metadata = {
      backup_id: backupId,
      timestamp: timestamp,
      created_at: new Date().toISOString(),
      version: '1.0.0',
      system: {
        node_version: process.version,
        platform: process.platform,
        arch: process.arch,
        uptime: process.uptime()
      },
      config: this.config,
      stats: this.backupStats
    };
    
    await fs.writeFile(
      path.join(backupDir, 'metadata.json'),
      JSON.stringify(metadata, null, 2)
    );
  }

  // Comprimir backup
  async compressBackup(tempDir, outputPath) {
    return new Promise((resolve, reject) => {
      const output = fs.createWriteStream(outputPath);
      const archive = archiver('zip', {
        zlib: { level: this.config.compressionLevel }
      });
      
      output.on('close', () => resolve(outputPath));
      archive.on('error', reject);
      
      archive.pipe(output);
      archive.directory(tempDir, false);
      archive.finalize();
    });
  }

  // Verificar integridad del backup
  async verifyBackup(backupPath) {
    const stats = await fs.stat(backupPath);
    const size = stats.size;
    
    if (size === 0) {
      throw new Error('Backup vacío o corrupto');
    }
    
    return size;
  }

  // Actualizar estadísticas de backup
  updateBackupStats(success, size) {
    this.backupStats.totalBackups++;
    
    if (success) {
      this.backupStats.successfulBackups++;
      this.backupStats.lastBackupSize = size;
      this.backupStats.totalBackupSize += size;
    } else {
      this.backupStats.failedBackups++;
    }
  }

  // Limpiar backups antiguos
  async cleanupOldBackups() {
    try {
      const files = await fs.readdir(this.config.backupDir);
      const backupFiles = files.filter(f => f.startsWith('chat_backup_') && f.endsWith('.zip'));
      
      if (backupFiles.length <= this.config.maxBackups) {
        return;
      }
      
      // Ordenar por fecha de creación
      const fileStats = await Promise.all(
        backupFiles.map(async (file) => {
          const filePath = path.join(this.config.backupDir, file);
          const stats = await fs.stat(filePath);
          return { file, filePath, created: stats.birthtime };
        })
      );
      
      fileStats.sort((a, b) => a.created - b.created);
      
      // Eliminar archivos antiguos
      const filesToDelete = fileStats.slice(0, fileStats.length - this.config.maxBackups);
      
      for (const fileInfo of filesToDelete) {
        await fs.unlink(fileInfo.filePath);
        console.log(`🗑️ Backup antiguo eliminado: ${fileInfo.file}`);
      }
      
    } catch (error) {
      console.error('Error limpiando backups antiguos:', error);
    }
  }

  // Restaurar backup
  async restoreBackup(backupPath) {
    try {
      console.log(`🔄 Iniciando restauración desde: ${backupPath}`);
      
      // Verificar que el archivo existe
      await fs.access(backupPath);
      
      // Crear directorio temporal para extracción
      const extractDir = path.join(this.config.backupDir, 'restore_temp', uuidv4());
      await fs.mkdir(extractDir, { recursive: true });
      
      // Extraer backup
      await this.extractBackup(backupPath, extractDir);
      
      // Leer metadatos
      const metadataPath = path.join(extractDir, 'metadata.json');
      const metadata = JSON.parse(await fs.readFile(metadataPath, 'utf8'));
      
      console.log(`📊 Restaurando backup del ${metadata.timestamp}`);
      
      // Aquí se implementaría la lógica de restauración a la base de datos
      // Por ahora solo mostramos la información
      console.log('✅ Backup extraído correctamente');
      console.log('📋 Para restaurar, implementar lógica de base de datos');
      
      // Limpiar directorio temporal
      await fs.rm(extractDir, { recursive: true, force: true });
      
    } catch (error) {
      console.error('❌ Error restaurando backup:', error);
      throw error;
    }
  }

  // Extraer backup
  async extractBackup(backupPath, extractDir) {
    // Esta función requeriría una librería como unzip o similar
    // Por ahora solo simulamos la extracción
    console.log(`📦 Extrayendo backup a: ${extractDir}`);
    
    // En una implementación real, aquí se extraería el archivo ZIP
    // Por simplicidad, solo copiamos los archivos si ya están extraídos
    try {
      const files = await fs.readdir(backupPath.replace('.zip', ''));
      for (const file of files) {
        const sourcePath = path.join(backupPath.replace('.zip', ''), file);
        const destPath = path.join(extractDir, file);
        await fs.copyFile(sourcePath, destPath);
      }
    } catch (error) {
      console.log('⚠️ Simulando extracción de backup...');
    }
  }

  // Obtener estadísticas de backup
  getBackupStats() {
    return {
      ...this.backupStats,
      lastBackupTime: this.lastBackupTime,
      nextScheduledBackup: this.lastBackupTime ? 
        new Date(this.lastBackupTime.getTime() + this.config.backupInterval) : null,
      backupInProgress: this.backupInProgress,
      config: this.config
    };
  }

  // Obtener lista de backups disponibles
  async getAvailableBackups() {
    try {
      const files = await fs.readdir(this.config.backupDir);
      const backupFiles = files.filter(f => f.startsWith('chat_backup_') && f.endsWith('.zip'));
      
      const backupInfo = await Promise.all(
        backupFiles.map(async (file) => {
          const filePath = path.join(this.config.backupDir, file);
          const stats = await fs.stat(filePath);
          
          return {
            filename: file,
            size: this.formatBytes(stats.size),
            sizeBytes: stats.size,
            created: stats.birthtime,
            modified: stats.mtime
          };
        })
      );
      
      return backupInfo.sort((a, b) => b.created - a.created);
      
    } catch (error) {
      console.error('Error obteniendo lista de backups:', error);
      return [];
    }
  }

  // Formatear bytes en formato legible
  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Forzar backup manual
  async forceBackup() {
    if (this.backupInProgress) {
      throw new Error('Backup ya en progreso');
    }
    
    console.log('🔄 Iniciando backup manual...');
    await this.createBackup();
  }
}

module.exports = ChatBackupSystem;
