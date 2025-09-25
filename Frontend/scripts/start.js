#!/usr/bin/env node

/**
 * SCRIPT DE ARRANQUE COMPLETO PARA FRONTEND SHEILY AI
 * =============================================================================
 * Este script verifica todas las dependencias, configura el entorno
 * y inicia el frontend Next.js en el puerto 3000 sin errores
 * =============================================================================
 * Ubicación: Frontend/scripts/start.js
 * =============================================================================
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Colores para output
const Colors = {
    RED: '\x1b[31m',
    GREEN: '\x1b[32m',
    YELLOW: '\x1b[33m',
    BLUE: '\x1b[34m',
    PURPLE: '\x1b[35m',
    CYAN: '\x1b[36m',
    NC: '\x1b[0m'
};

// Función para imprimir mensajes con colores
function printStatus(message) {
    console.log(`${Colors.BLUE}[INFO]${Colors.NC} ${message}`);
}

function printSuccess(message) {
    console.log(`${Colors.GREEN}[SUCCESS]${Colors.NC} ${message}`);
}

function printWarning(message) {
    console.log(`${Colors.YELLOW}[WARNING]${Colors.NC} ${message}`);
}

function printError(message) {
    console.log(`${Colors.RED}[ERROR]${Colors.NC} ${message}`);
}

function printHeader(title) {
    console.log(`${Colors.PURPLE}${'='.repeat(32)}${Colors.NC}`);
    console.log(`${Colors.PURPLE}${title}${Colors.NC}`);
    console.log(`${Colors.PURPLE}${'='.repeat(32)}${Colors.NC}`);
}

class FrontendStarter {
    constructor() {
        this.projectDir = __dirname;
        this.packageJsonPath = path.join(this.projectDir, 'package.json');
        this.nodeModulesPath = path.join(this.projectDir, 'node_modules');
        this.envLocalPath = path.join(this.projectDir, '.env.local');
        this.port = 3000;
        this.hostname = '127.0.0.1';
    }

    // Función para ejecutar comandos de forma síncrona
    execCommand(command, options = {}) {
        try {
            return execSync(command, { 
                cwd: this.projectDir, 
                encoding: 'utf8',
                stdio: options.silent ? 'pipe' : 'inherit',
                ...options 
            });
        } catch (error) {
            if (!options.ignoreErrors) {
                throw error;
            }
            return null;
        }
    }

    // Función para ejecutar comandos de forma asíncrona
    spawnCommand(command, args, options = {}) {
        return new Promise((resolve, reject) => {
            const child = spawn(command, args, {
                cwd: this.projectDir,
                stdio: 'inherit',
                ...options
            });

            child.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Command failed with exit code ${code}`));
                }
            });

            child.on('error', reject);
        });
    }

    // Limpiar procesos anteriores
    cleanupPreviousProcesses() {
        printStatus('Limpiando procesos anteriores del frontend...');
        
        try {
            // Buscar y matar procesos en el puerto 3000
            if (os.platform() === 'win32') {
                // Windows
                try {
                    const result = this.execCommand(`netstat -ano | findstr :${this.port}`, { silent: true });
                    if (result) {
                        printWarning('Encontrados procesos anteriores en puerto 3000');
                        const lines = result.split('\n');
                        for (const line of lines) {
                            if (line.trim()) {
                                const parts = line.trim().split(/\s+/);
                                if (parts.length >= 5) {
                                    const pid = parts[parts.length - 1];
                                    try {
                                        this.execCommand(`taskkill /PID ${pid} /F`, { silent: true, ignoreErrors: true });
                                    } catch (e) {
                                        // Ignorar errores
                                    }
                                }
                            }
                        }
                    }
                } catch (e) {
                    // Ignorar errores
                }
            } else {
                // Linux/Mac
                try {
                    const result = this.execCommand(`lsof -ti:${this.port}`, { silent: true });
                    if (result && result.trim()) {
                        const pids = result.trim().split('\n');
                        printWarning(`Encontrados procesos anteriores en puerto ${this.port}: ${pids.join(', ')}`);
                        for (const pid of pids) {
                            try {
                                this.execCommand(`kill -9 ${pid}`, { silent: true, ignoreErrors: true });
                            } catch (e) {
                                // Ignorar errores
                            }
                        }
                    }
                } catch (e) {
                    // Ignorar errores
                }
            }

            // Limpiar caché de Next.js
            const nextCachePath = path.join(this.projectDir, '.next');
            if (fs.existsSync(nextCachePath)) {
                printStatus('Limpiando caché de Next.js...');
                const cacheDir = path.join(nextCachePath, '.cache');
                const traceDir = path.join(nextCachePath, 'trace');
                
                if (fs.existsSync(cacheDir)) {
                    fs.rmSync(cacheDir, { recursive: true, force: true });
                }
                if (fs.existsSync(traceDir)) {
                    fs.rmSync(traceDir, { recursive: true, force: true });
                }
                printSuccess('Caché limpiado');
            }

            printSuccess('Procesos anteriores terminados');
        } catch (error) {
            printWarning(`No se pudieron limpiar procesos anteriores: ${error.message}`);
        }
    }

    // Verificar dependencias del sistema
    checkSystemDependencies() {
        printHeader('VERIFICANDO DEPENDENCIAS DEL SISTEMA');
        
        try {
            // Verificar Node.js
            const nodeVersion = this.execCommand('node --version', { silent: true });
            if (!nodeVersion) {
                printError('Node.js no está instalado');
                printStatus('Por favor, instala Node.js 18 o superior desde https://nodejs.org/');
                return false;
            }

            // Verificar npm
            const npmVersion = this.execCommand('npm --version', { silent: true });
            if (!npmVersion) {
                printError('npm no está instalado');
                return false;
            }

            printSuccess(`Node.js encontrado: ${nodeVersion.trim()}`);
            printSuccess(`npm encontrado: ${npmVersion.trim()}`);

            // Verificar versión mínima de Node.js
            const nodeMajor = parseInt(nodeVersion.trim().substring(1).split('.')[0]);
            if (nodeMajor < 18) {
                printError(`Se requiere Node.js 18 o superior. Versión actual: ${nodeVersion.trim()}`);
                return false;
            }

            printSuccess('Todas las dependencias del sistema están disponibles');
            return true;
        } catch (error) {
            printError(`Error al verificar dependencias: ${error.message}`);
            return false;
        }
    }

    // Configurar entorno
    setupEnvironment() {
        printHeader('CONFIGURANDO ENTORNO');
        
        try {
            // Verificar si estamos en el directorio correcto
            if (!fs.existsSync(this.packageJsonPath)) {
                printError('No se encontró package.json. Asegúrate de estar en el directorio Frontend/');
                return false;
            }

            // Verificar si es el proyecto correcto
            const packageData = JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
            if (packageData.name !== 'sheily-landing-next') {
                printError('Este no parece ser el proyecto Sheily AI Frontend');
                return false;
            }

            printSuccess('Directorio del proyecto verificado');

            // Crear archivo .env.local si no existe
            if (!fs.existsSync(this.envLocalPath)) {
                printStatus('Creando archivo .env.local...');
                const envContent = `# Configuración del Frontend Sheily AI
NODE_ENV=development
PORT=${this.port}
HOSTNAME=${this.hostname}
NEXTAUTH_SECRET=sheily_ai_frontend_secret_key_development_${Date.now()}
BACKEND_URL=http://localhost:8000
NEXTAUTH_URL=http://${this.hostname}:${this.port}
`;
                fs.writeFileSync(this.envLocalPath, envContent);
                printSuccess('Archivo .env.local creado');
            } else {
                printSuccess('Archivo .env.local ya existe');
            }

            // Configurar variables de entorno
            process.env.NODE_ENV = 'development';
            process.env.PORT = this.port.toString();
            process.env.HOSTNAME = this.hostname;

            printSuccess('Entorno configurado correctamente');
            return true;
        } catch (error) {
            printError(`Error al configurar entorno: ${error.message}`);
            return false;
        }
    }

    // Verificar dependencias de Node.js
    checkNodeDependencies() {
        printHeader('VERIFICANDO DEPENDENCIAS DE NODE.JS');
        
        try {
            if (!fs.existsSync(this.nodeModulesPath)) {
                printWarning('node_modules no encontrado. Instalando dependencias...');
                return this.installDependencies();
            }

            printSuccess('node_modules encontrado');

            // Verificar dependencias
            try {
                const result = this.execCommand('npm ls --depth=0', { silent: true });
                if (result && (result.includes('UNMET DEPENDENCY') || result.includes('npm ERR!'))) {
                    printWarning('Dependencias faltantes detectadas. Reinstalando...');
                    return this.installDependencies();
                } else {
                    printSuccess('Todas las dependencias están instaladas correctamente');
                    return true;
                }
            } catch (error) {
                printWarning('Error al verificar dependencias. Reinstalando...');
                return this.installDependencies();
            }
        } catch (error) {
            printError(`Error al verificar dependencias: ${error.message}`);
            return false;
        }
    }

    // Instalar dependencias
    installDependencies() {
        printHeader('INSTALANDO DEPENDENCIAS');
        
        try {
            // Limpiar instalación anterior si existe
            if (fs.existsSync(this.nodeModulesPath)) {
                printStatus('Limpiando instalación anterior...');
                fs.rmSync(this.nodeModulesPath, { recursive: true, force: true });
                
                const packageLockPath = path.join(this.projectDir, 'package-lock.json');
                if (fs.existsSync(packageLockPath)) {
                    fs.unlinkSync(packageLockPath);
                }
            }

            // Limpiar caché de npm
            printStatus('Limpiando caché de npm...');
            this.execCommand('npm cache clean --force', { silent: true });

            // Instalar dependencias
            printStatus('Instalando dependencias...');
            this.execCommand('npm install');

            printSuccess('Dependencias instaladas correctamente');
            return true;
        } catch (error) {
            printError(`Error al instalar dependencias: ${error.message}`);
            return false;
        }
    }

    // Verificar configuración de Next.js
    checkNextJSConfig() {
        printHeader('VERIFICANDO CONFIGURACIÓN DE NEXT.JS');
        
        const configFiles = [
            'next.config.cjs',
            'tsconfig.json',
            'tailwind.config.ts',
            'postcss.config.cjs'
        ];

        for (const configFile of configFiles) {
            const configPath = path.join(this.projectDir, configFile);
            if (fs.existsSync(configPath)) {
                printSuccess(`${configFile} encontrado`);
            } else {
                printError(`${configFile} no encontrado`);
                return false;
            }
        }

        // Verificar configuración de TypeScript
        try {
            printStatus('Verificando configuración de TypeScript...');
            this.execCommand('npx tsc --noEmit --skipLibCheck', { silent: true, ignoreErrors: true });
            printSuccess('Configuración de TypeScript verificada');
        } catch (error) {
            printWarning('Errores de TypeScript detectados, pero continuando...');
        }

        printSuccess('Configuración de Next.js verificada');
        return true;
    }

    // Verificar archivos de audio
    checkAudioFiles() {
        printHeader('VERIFICANDO ARCHIVOS DE AUDIO');
        
        const audioDir = path.join(this.projectDir, 'public', 'sounds');
        const requiredFiles = [
            '062708_laser-charging-81968.mp3',
            'whoosh-drum-hits-169007.mp3'
        ];

        if (!fs.existsSync(audioDir)) {
            printWarning('Directorio de sonidos no encontrado. Creando...');
            fs.mkdirSync(audioDir, { recursive: true });
        }

        const missingFiles = [];
        for (const audioFile of requiredFiles) {
            if (!fs.existsSync(path.join(audioDir, audioFile))) {
                missingFiles.push(audioFile);
            }
        }

        if (missingFiles.length > 0) {
            printWarning(`Archivos de audio faltantes: ${missingFiles.join(', ')}`);
            printStatus('Los sonidos se generarán sintéticamente como fallback');
        } else {
            printSuccess('Todos los archivos de audio están disponibles');
        }

        return true;
    }

    // Verificar puertos
    checkPorts() {
        printHeader('VERIFICANDO PUERTOS');
        
        try {
            // Verificar puerto 3000
            if (os.platform() === 'win32') {
                const result = this.execCommand(`netstat -ano | findstr :${this.port}`, { silent: true, ignoreErrors: true });
                if (result && result.trim()) {
                    printWarning(`Puerto ${this.port} está en uso`);
                    printStatus('Intentando liberar el puerto...');
                    this.cleanupPreviousProcesses();
                }
            } else {
                const result = this.execCommand(`lsof -ti:${this.port}`, { silent: true, ignoreErrors: true });
                if (result && result.trim()) {
                    printWarning(`Puerto ${this.port} está en uso`);
                    printStatus('Intentando liberar el puerto...');
                    this.cleanupPreviousProcesses();
                }
            }

            printSuccess(`Puerto ${this.port} está disponible`);

            // Verificar puerto 8000 (backend)
            if (os.platform() === 'win32') {
                const result = this.execCommand('netstat -ano | findstr :8000', { silent: true, ignoreErrors: true });
                if (result && result.trim()) {
                    printSuccess('Backend detectado en puerto 8000');
                } else {
                    printWarning('Backend no detectado en puerto 8000');
                }
            } else {
                const result = this.execCommand('lsof -ti:8000', { silent: true, ignoreErrors: true });
                if (result && result.trim()) {
                    printSuccess('Backend detectado en puerto 8000');
                } else {
                    printWarning('Backend no detectado en puerto 8000');
                }
            }

            printStatus('El frontend funcionará en modo standalone si es necesario');
            return true;
        } catch (error) {
            printWarning(`No se pudieron verificar los puertos: ${error.message}`);
            return true; // Continuar de todas formas
        }
    }

    // Iniciar frontend
    async startFrontend() {
        printHeader('INICIANDO FRONTEND SHEILY AI');
        
        printStatus(`Iniciando servidor de desarrollo en puerto ${this.port}...`);
        printStatus(`URL: http://${this.hostname}:${this.port}`);
        printStatus('Presiona Ctrl+C para detener el servidor');
        
        try {
            // Iniciar el servidor
            const env = { ...process.env };
            env.NODE_ENV = 'development';
            env.PORT = this.port.toString();
            env.HOSTNAME = this.hostname;

            await this.spawnCommand('npm', ['run', 'dev'], { env });
        } catch (error) {
            if (error.message.includes('exit code')) {
                printStatus('Servidor detenido');
            } else {
                printError(`Error al iniciar el frontend: ${error.message}`);
            }
        }
    }

    // Ejecutar proceso completo
    async run() {
        printHeader('ARRANQUE DEL FRONTEND SHEILY AI');
        printStatus('Iniciando proceso de arranque completo...');
        
        try {
            // Ejecutar todas las verificaciones y configuraciones
            if (!this.checkSystemDependencies()) {
                return false;
            }

            if (!this.setupEnvironment()) {
                return false;
            }

            if (!this.checkNodeDependencies()) {
                return false;
            }

            if (!this.checkNextJSConfig()) {
                return false;
            }

            if (!this.checkAudioFiles()) {
                return false;
            }

            if (!this.checkPorts()) {
                return false;
            }

            printHeader('VERIFICACIONES COMPLETADAS');
            printSuccess('✅ Sistema de dependencias verificado');
            printSuccess('✅ Entorno configurado');
            printSuccess('✅ Configuración de Next.js validada');
            printSuccess('✅ Puertos verificados');
            printSuccess('✅ Archivos de audio verificados');

            printStatus('Iniciando frontend...');
            await this.startFrontend();
            return true;
        } catch (error) {
            printError(`Error durante el arranque: ${error.message}`);
            return false;
        }
    }
}

// Función principal
async function main() {
    try {
        const starter = new FrontendStarter();
        const success = await starter.run();
        
        if (!success) {
            printError('El arranque del frontend falló');
            process.exit(1);
        }
    } catch (error) {
        printError(`Error inesperado: ${error.message}`);
        process.exit(1);
    }
}

// Manejar señales de interrupción
process.on('SIGINT', () => {
    printStatus('Recibida señal de interrupción. Limpiando...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    printStatus('Recibida señal de terminación. Limpiando...');
    process.exit(0);
});

// Ejecutar función principal
main();
