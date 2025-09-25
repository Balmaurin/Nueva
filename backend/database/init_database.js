#!/usr/bin/env node
/**
 * Inicializador de Base de Datos - Sheily AI
 * ==========================================
 * Inicializa la base de datos con las 35 ramas especializadas
 */

// Importar el gestor de base de datos Python
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class DatabaseInitializer {
    constructor() {
        this.projectRoot = path.join(__dirname, '../..');
    }

    async initialize() {
        console.log('🚀 Inicializando base de datos Sheily AI...');
        
        try {
            // 1. Ejecutar inicialización Python
            console.log('📋 Ejecutando inicialización Python...');
            const pythonResult = await this.runPythonInitialization();
            if (!pythonResult) {
                throw new Error('Error en inicialización Python');
            }
            console.log('✅ Inicialización Python completada');

            // 2. Crear usuario administrador por defecto
            console.log('👤 Creando usuario administrador...');
            await this.createAdminUser();

            // 3. Verificar inicialización
            console.log('🔍 Verificando inicialización...');
            const info = await this.getDatabaseInfo();
            console.log('📊 Información de la base de datos:');
            console.log(`   - Tipo: ${info.type}`);
            console.log(`   - Tablas: ${info.tables.length}`);
            console.log(`   - Ramas: ${info.branches_count}`);
            console.log(`   - Usuarios: ${info.users_count}`);

            console.log('🎉 Base de datos inicializada exitosamente!');
            return true;

        } catch (error) {
            console.error('❌ Error inicializando base de datos:', error.message);
            return false;
        }
    }

    async runPythonInitialization() {
        return new Promise((resolve) => {
            const pythonProcess = spawn('python3', [
                path.join(this.projectRoot, 'backend/database/database_manager.py')
            ], {
                cwd: this.projectRoot,
                stdio: 'inherit'
            });

            pythonProcess.on('close', (code) => {
                resolve(code === 0);
            });

            pythonProcess.on('error', (error) => {
                console.error('❌ Error ejecutando Python:', error);
                resolve(false);
            });
        });
    }

    async getDatabaseInfo() {
        return new Promise((resolve) => {
            const pythonProcess = spawn('python3', [
                '-c',
                `
import sys
sys.path.append('.')
from backend.database.database_manager import db_manager
info = db_manager.get_database_info()
print(f"TYPE:{info.get('type', 'unknown')}")
print(f"TABLES:{len(info.get('tables', []))}")
print(f"BRANCHES:{info.get('branches_count', 0)}")
print(f"USERS:{info.get('users_count', 0)}")
                `
            ], {
                cwd: this.projectRoot,
                stdio: 'pipe'
            });

            let output = '';
            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code === 0) {
                    const lines = output.trim().split('\n');
                    const info = {};
                    lines.forEach(line => {
                        const [key, value] = line.split(':');
                        if (key === 'TYPE') info.type = value;
                        else if (key === 'TABLES') info.tables = Array(parseInt(value)).fill('table');
                        else if (key === 'BRANCHES') info.branches_count = parseInt(value);
                        else if (key === 'USERS') info.users_count = parseInt(value);
                    });
                    resolve(info);
                } else {
                    resolve({ type: 'unknown', tables: [], branches_count: 0, users_count: 0 });
                }
            });
        });
    }

    async createAdminUser() {
        try {
            const bcrypt = require('bcryptjs');
            
            // Verificar si ya existe un usuario admin
            const existingAdmin = this.dbManager.execute_query(
                "SELECT id FROM users WHERE username = ? OR email = ?",
                ['admin', 'admin@sheily-ai.com']
            );

            if (existingAdmin.length > 0) {
                console.log('✅ Usuario administrador ya existe');
                return;
            }

            // Crear usuario administrador
            const hashedPassword = await bcrypt.hash('SheilyAI2025!', 12);
            
            this.dbManager.execute_query(
                `INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)`,
                ['admin', 'admin@sheily-ai.com', hashedPassword, 'admin']
            );

            console.log('✅ Usuario administrador creado');
            console.log('   - Usuario: admin');
            console.log('   - Email: admin@sheily-ai.com');
            console.log('   - Contraseña: SheilyAI2025!');
            console.log('   - Rol: admin');

        } catch (error) {
            console.error('❌ Error creando usuario administrador:', error.message);
        }
    }

    async createSampleExercises() {
        try {
            console.log('📝 Creando ejercicios de muestra...');
            
            // Obtener ramas
            const branches = this.dbManager.execute_query("SELECT id, name FROM branches LIMIT 5");
            
            for (const branch of branches) {
                // Crear ejercicios de muestra para cada rama
                const exerciseTypes = ['yes_no', 'true_false', 'multiple_choice'];
                
                for (let level = 1; level <= 3; level++) {
                    for (const type of exerciseTypes) {
                        const question = this.generateSampleQuestion(branch.name, type, level);
                        
                        // Insertar ejercicio
                        const result = this.dbManager.execute_query(
                            `INSERT INTO branch_exercises (branch_id, type, level, question) VALUES (?, ?, ?, ?)`,
                            [branch.id, type, level, question]
                        );

                        if (result.length > 0) {
                            const exerciseId = result[0].lastID || result[0].id;
                            
                            // Crear respuestas
                            this.createSampleAnswers(exerciseId, type, branch.name);
                        }
                    }
                }
            }

            console.log('✅ Ejercicios de muestra creados');

        } catch (error) {
            console.error('❌ Error creando ejercicios de muestra:', error.message);
        }
    }

    generateSampleQuestion(branchName, type, level) {
        const questions = {
            'yes_no': `¿Es correcto que en ${branchName} se aplican principios fundamentales?`,
            'true_false': `En ${branchName}, los conceptos básicos son esenciales para el aprendizaje.`,
            'multiple_choice': `¿Cuál es el aspecto más importante de ${branchName}?`
        };
        return questions[type] || `Pregunta de muestra para ${branchName}`;
    }

    createSampleAnswers(exerciseId, type, branchName) {
        const answers = {
            'yes_no': [
                { answer: 'Sí', is_correct: true, explanation: 'Correcto, los principios fundamentales son la base.' },
                { answer: 'No', is_correct: false, explanation: 'Incorrecto, los principios son esenciales.' }
            ],
            'true_false': [
                { answer: 'Verdadero', is_correct: true, explanation: 'Correcto, los conceptos básicos son fundamentales.' },
                { answer: 'Falso', is_correct: false, explanation: 'Incorrecto, los conceptos básicos son importantes.' }
            ],
            'multiple_choice': [
                { answer: 'Los fundamentos teóricos', is_correct: true, explanation: 'Correcto, la teoría es la base.' },
                { answer: 'La práctica sin teoría', is_correct: false, explanation: 'Incorrecto, se necesita teoría.' },
                { answer: 'Solo la memorización', is_correct: false, explanation: 'Incorrecto, se necesita comprensión.' },
                { answer: 'La improvisación', is_correct: false, explanation: 'Incorrecto, se necesita estructura.' }
            ]
        };

        const answerSet = answers[type] || [];
        
        for (const answerData of answerSet) {
            this.dbManager.execute_query(
                `INSERT INTO branch_exercise_answers (exercise_id, answer, is_correct, explanation) VALUES (?, ?, ?, ?)`,
                [exerciseId, answerData.answer, answerData.is_correct, answerData.explanation]
            );
        }
    }
}

// Función principal
async function main() {
    const initializer = new DatabaseInitializer();
    
    console.log('🚀 Inicializador de Base de Datos - Sheily AI');
    console.log('=' .repeat(50));
    
    const success = await initializer.initialize();
    
    if (success) {
        console.log('\n🎉 ¡Inicialización completada exitosamente!');
        console.log('\n📋 Próximos pasos:');
        console.log('1. Iniciar el servidor: npm start');
        console.log('2. Acceder al dashboard: http://localhost:3000');
        console.log('3. Iniciar sesión con: admin / SheilyAI2025!');
        process.exit(0);
    } else {
        console.log('\n❌ Error en la inicialización');
        process.exit(1);
    }
}

// Ejecutar si es llamado directamente
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Error fatal:', error);
        process.exit(1);
    });
}

module.exports = DatabaseInitializer;
