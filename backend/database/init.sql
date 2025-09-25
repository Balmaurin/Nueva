-- Establecer propietario de esquema
ALTER SCHEMA public OWNER TO sheily_ai_user;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    reset_password_token VARCHAR(255),
    reset_password_expires TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE users OWNER TO sheily_ai_user;

-- Tabla de tokens de usuario
CREATE TABLE IF NOT EXISTS user_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    tokens INTEGER DEFAULT 100,
    earned_tokens INTEGER DEFAULT 0,
    spent_tokens INTEGER DEFAULT 0,
    token_type VARCHAR(50) DEFAULT 'standard',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE user_tokens OWNER TO sheily_ai_user;

-- Tabla de sesiones de entrenamiento
CREATE TABLE IF NOT EXISTS training_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    branch_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_exercises INTEGER DEFAULT 0,
    completed_exercises INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    model_config JSONB,
    metrics JSONB,
    model_details JSONB DEFAULT '{"baseModel": "Phi-3-mini", "quantization": "4bit", "domain": "general"}'
);

-- Establecer propietario de tabla
ALTER TABLE training_sessions OWNER TO sheily_ai_user;

-- Tabla de mensajes de chat
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE chat_messages OWNER TO sheily_ai_user;

-- Tabla de sesiones de chat
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(100) DEFAULT 'phi3-mini-4bit',
    total_messages INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0
);

-- Establecer propietario de tabla
ALTER TABLE chat_sessions OWNER TO sheily_ai_user;

-- Tabla de conversaciones de chat
CREATE TABLE IF NOT EXISTS chat_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    response_time FLOAT NOT NULL,
    tokens_used INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE chat_conversations OWNER TO sheily_ai_user;

-- Tabla de ramas principales
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    keywords TEXT[],
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE branches OWNER TO sheily_ai_user;

-- Tabla de transacciones de bóveda
CREATE TABLE IF NOT EXISTS vault_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE vault_transactions OWNER TO sheily_ai_user;

-- Tabla de logs del sistema
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    log_level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE system_logs OWNER TO sheily_ai_user;

-- Tabla de registro de modelos
CREATE TABLE IF NOT EXISTS model_registry (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(100) NOT NULL,
    base_model VARCHAR(255),
    training_dataset VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_training_date TIMESTAMP WITH TIME ZONE,
    total_training_time INTEGER,
    dataset_size INTEGER,
    model_size_mb FLOAT,
    hardware_used VARCHAR(50),
    version VARCHAR(50),
    description TEXT,
    performance_metrics JSONB,
    model_details JSONB
);

-- Establecer propietario de tabla
ALTER TABLE model_registry OWNER TO sheily_ai_user;

-- Tabla de métricas de entrenamiento por época
CREATE TABLE IF NOT EXISTS model_training_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    epoch INTEGER NOT NULL,
    accuracy FLOAT,
    loss FLOAT,
    f1_score FLOAT,
    learning_rate FLOAT,
    batch_size INTEGER,
    training_time_seconds FLOAT,
    memory_usage_mb FLOAT,
    gpu_utilization FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_name) REFERENCES model_registry(name) ON DELETE CASCADE
);

-- Establecer propietario de tabla
ALTER TABLE model_training_metrics OWNER TO sheily_ai_user;

-- Tabla de ejercicios de entrenamiento
CREATE TABLE IF NOT EXISTS training_exercises (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES training_sessions(session_id) ON DELETE CASCADE,
    exercise_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT,
    correct_answer TEXT NOT NULL,
    is_correct BOOLEAN,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE training_exercises OWNER TO sheily_ai_user;

-- Tabla de ejercicios generados por rama y ámbito
CREATE TABLE IF NOT EXISTS branch_exercises (
    id SERIAL PRIMARY KEY,
    branch_id VARCHAR(50) NOT NULL,
    branch_name VARCHAR(255) NOT NULL,
    scope VARCHAR(255) NOT NULL,
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 20),
    exercise_type VARCHAR(32) NOT NULL CHECK (exercise_type IN ('yes_no', 'true_false', 'multiple_choice')),
    question TEXT NOT NULL,
    options JSONB,
    metadata JSONB DEFAULT '{}',
    competency VARCHAR(255) DEFAULT 'general',
    difficulty VARCHAR(50) DEFAULT 'standard',
    objective TEXT,
    reference_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(branch_id, scope, level, exercise_type)
);

-- Establecer propietario de tabla
ALTER TABLE branch_exercises OWNER TO sheily_ai_user;

-- Tabla de respuestas oficiales de ejercicios por rama
CREATE TABLE IF NOT EXISTS branch_exercise_answers (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES branch_exercises(id) ON DELETE CASCADE,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    validation_source TEXT,
    confidence_score NUMERIC(5,2) CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE branch_exercise_answers OWNER TO sheily_ai_user;

ALTER TABLE branch_exercises
    ADD COLUMN IF NOT EXISTS competency VARCHAR(255) DEFAULT 'general';

ALTER TABLE branch_exercises
    ADD COLUMN IF NOT EXISTS difficulty VARCHAR(50) DEFAULT 'standard';

ALTER TABLE branch_exercises
    ADD COLUMN IF NOT EXISTS objective TEXT;

ALTER TABLE branch_exercises
    ADD COLUMN IF NOT EXISTS reference_url TEXT;

ALTER TABLE branch_exercise_answers
    ADD COLUMN IF NOT EXISTS validation_source TEXT;

ALTER TABLE branch_exercise_answers
    ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(5,2) CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100));

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'branch_exercises_branch_id_fkey'
          AND table_name = 'branch_exercises'
    ) THEN
        ALTER TABLE branch_exercises
            ADD CONSTRAINT branch_exercises_branch_id_fkey
            FOREIGN KEY (branch_id)
            REFERENCES branches(id)
            ON DELETE CASCADE;
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'branch_exercise_answers_unique_exercise'
          AND table_name = 'branch_exercise_answers'
    ) THEN
        ALTER TABLE branch_exercise_answers
            ADD CONSTRAINT branch_exercise_answers_unique_exercise
            UNIQUE (exercise_id);
    END IF;
END;
$$;

-- Tabla de opciones detalladas para ejercicios de respuesta múltiple
CREATE TABLE IF NOT EXISTS branch_exercise_options (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES branch_exercises(id) ON DELETE CASCADE,
    option_key VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exercise_id, option_key)
);

ALTER TABLE branch_exercise_options OWNER TO sheily_ai_user;

-- Tabla de intentos de usuarios sobre ejercicios de ramas
CREATE TABLE IF NOT EXISTS user_branch_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES branch_exercises(id) ON DELETE CASCADE,
    exercise_type VARCHAR(32) NOT NULL CHECK (exercise_type IN ('yes_no', 'true_false', 'multiple_choice')),
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 20),
    submitted_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    accuracy NUMERIC(5,2) CHECK (accuracy >= 0 AND accuracy <= 100),
    score NUMERIC(6,2) DEFAULT 0,
    validation_source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_branch_attempts OWNER TO sheily_ai_user;

-- Tabla de progreso agregado por usuario y rama
CREATE TABLE IF NOT EXISTS user_branch_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    exercise_type VARCHAR(32) NOT NULL CHECK (exercise_type IN ('yes_no', 'true_false', 'multiple_choice')),
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 20),
    accuracy NUMERIC(5,2) DEFAULT 0 CHECK (accuracy >= 0 AND accuracy <= 100),
    attempts INTEGER DEFAULT 0 CHECK (attempts >= 0),
    completed BOOLEAN DEFAULT FALSE,
    tokens_awarded INTEGER DEFAULT 0 CHECK (tokens_awarded >= 0),
    verification_status VARCHAR(32) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'in_review', 'verified', 'rejected')),
    verification_source TEXT,
    dataset_snapshot JSONB DEFAULT '{}',
    last_reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, branch_id, exercise_type, level)
);

ALTER TABLE user_branch_progress OWNER TO sheily_ai_user;

-- Tabla de prompts
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    tags TEXT[] DEFAULT '{}',
    model_type VARCHAR(100) DEFAULT 'general',
    complexity VARCHAR(50) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE prompts OWNER TO sheily_ai_user;

-- Tabla de evaluaciones de prompts
CREATE TABLE IF NOT EXISTS prompt_evaluations (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    model_name VARCHAR(255) NOT NULL,
    metrics JSONB NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Establecer propietario de tabla
ALTER TABLE prompt_evaluations OWNER TO sheily_ai_user;

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_user_tokens_user_id ON user_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_user_id ON training_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_model_registry_name ON model_registry(name);
CREATE INDEX IF NOT EXISTS idx_model_registry_status ON model_registry(status);
CREATE INDEX IF NOT EXISTS idx_model_training_metrics_model_name ON model_training_metrics(model_name);
CREATE INDEX IF NOT EXISTS idx_model_training_metrics_epoch ON model_training_metrics(epoch);
CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_model_type ON prompts(model_type);
CREATE INDEX IF NOT EXISTS idx_branch_exercises_branch_scope ON branch_exercises(branch_id, scope);
CREATE INDEX IF NOT EXISTS idx_branch_exercises_level ON branch_exercises(level);
CREATE INDEX IF NOT EXISTS idx_branch_exercise_answers_exercise_id ON branch_exercise_answers(exercise_id);
CREATE INDEX IF NOT EXISTS idx_branch_exercise_options_exercise_id ON branch_exercise_options(exercise_id);
CREATE INDEX IF NOT EXISTS idx_branch_exercise_options_option_key ON branch_exercise_options(option_key);
CREATE INDEX IF NOT EXISTS idx_user_branch_attempts_user_branch ON user_branch_attempts(user_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_user_branch_attempts_exercise ON user_branch_attempts(exercise_id);
CREATE INDEX IF NOT EXISTS idx_user_branch_progress_user_branch ON user_branch_progress(user_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_user_branch_progress_status ON user_branch_progress(verification_status);
CREATE INDEX IF NOT EXISTS idx_user_branch_progress_completion ON user_branch_progress(completed, accuracy);

-- Función para insertar métricas de entrenamiento
CREATE OR REPLACE FUNCTION insert_training_metrics(
    p_model_name VARCHAR(255),
    p_epoch INTEGER,
    p_accuracy FLOAT,
    p_loss FLOAT,
    p_f1_score FLOAT,
    p_learning_rate FLOAT DEFAULT NULL,
    p_batch_size INTEGER DEFAULT NULL,
    p_training_time_seconds FLOAT DEFAULT NULL,
    p_memory_usage_mb FLOAT DEFAULT NULL,
    p_gpu_utilization FLOAT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO model_training_metrics (
        model_name, epoch, accuracy, loss, f1_score, 
        learning_rate, batch_size, training_time_seconds, 
        memory_usage_mb, gpu_utilization
    ) VALUES (
        p_model_name, p_epoch, p_accuracy, p_loss, p_f1_score,
        p_learning_rate, p_batch_size, p_training_time_seconds,
        p_memory_usage_mb, p_gpu_utilization
    );
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar registro de modelo después del entrenamiento
CREATE OR REPLACE FUNCTION update_model_registry(
    p_name VARCHAR(255),
    p_type VARCHAR(100),
    p_base_model VARCHAR(255) DEFAULT NULL,
    p_training_dataset VARCHAR(255) DEFAULT NULL,
    p_total_training_time INTEGER DEFAULT NULL,
    p_dataset_size INTEGER DEFAULT NULL,
    p_model_size_mb FLOAT DEFAULT NULL,
    p_hardware_used VARCHAR(50) DEFAULT NULL,
    p_version VARCHAR(50) DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_performance_metrics JSONB DEFAULT NULL,
    p_model_details JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Insertar o actualizar modelo en el registro
    INSERT INTO model_registry (
        name, type, base_model, training_dataset, status, 
        last_training_date, total_training_time, dataset_size, 
        model_size_mb, hardware_used, version, description, 
        performance_metrics, model_details
    ) VALUES (
        p_name, p_type, p_base_model, p_training_dataset, 'trained', 
        CURRENT_TIMESTAMP, p_total_training_time, p_dataset_size, 
        p_model_size_mb, p_hardware_used, p_version, p_description, 
        p_performance_metrics, p_model_details
    )
    ON CONFLICT (name) DO UPDATE SET
        type = EXCLUDED.type,
        base_model = EXCLUDED.base_model,
        training_dataset = EXCLUDED.training_dataset,
        status = 'trained',
        last_training_date = CURRENT_TIMESTAMP,
        total_training_time = EXCLUDED.total_training_time,
        dataset_size = EXCLUDED.dataset_size,
        model_size_mb = EXCLUDED.model_size_mb,
        hardware_used = EXCLUDED.hardware_used,
        version = EXCLUDED.version,
        description = EXCLUDED.description,
        performance_metrics = EXCLUDED.performance_metrics,
        model_details = EXCLUDED.model_details;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar timestamp de actualización
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Eliminar triggers existentes antes de crearlos
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_user_tokens_updated_at ON user_tokens;
DROP TRIGGER IF EXISTS update_prompts_updated_at ON prompts;
DROP TRIGGER IF EXISTS update_branches_updated_at ON branches;
DROP TRIGGER IF EXISTS update_branch_exercises_updated_at ON branch_exercises;
DROP TRIGGER IF EXISTS update_user_branch_progress_updated_at ON user_branch_progress;

-- Triggers para actualizar timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_tokens_updated_at BEFORE UPDATE ON user_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompts_updated_at BEFORE UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_branches_updated_at BEFORE UPDATE ON branches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_branch_exercises_updated_at BEFORE UPDATE ON branch_exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_branch_progress_updated_at BEFORE UPDATE ON user_branch_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Datos iniciales de ejemplo
DO $$
BEGIN
    INSERT INTO branches (name, description, keywords, enabled)
    VALUES
        ('lengua_y_lingüística', 'Rama especializada en lengua y lingüística', ARRAY['gramática', 'sintaxis', 'semántica', 'lingüística', 'idioma'], true),
        ('matemáticas', 'Rama especializada en matemáticas', ARRAY['matemáticas', 'álgebra', 'cálculo', 'geometría', 'estadística'], true),
        ('computación_y_programación', 'Rama especializada en computación y programación', ARRAY['programación', 'algoritmos', 'desarrollo', 'software', 'computación'], true),
        ('medicina_y_salud', 'Rama especializada en medicina y salud', ARRAY['medicina', 'salud', 'anatomía', 'fisiología', 'enfermedades'], true),
        ('física', 'Rama especializada en física', ARRAY['física', 'mecánica', 'electromagnetismo', 'óptica', 'termodinámica'], true),
        ('química', 'Rama especializada en química', ARRAY['química', 'reacciones', 'compuestos', 'laboratorio', 'moléculas'], true),
        ('biología', 'Rama especializada en biología', ARRAY['biología', 'celular', 'genética', 'ecología', 'evolución'], true),
        ('historia', 'Rama especializada en historia', ARRAY['historia', 'civilizaciones', 'eventos', 'cronología', 'cultura'], true),
        ('geografía_y_geo_política', 'Rama especializada en geografía y geo-política', ARRAY['geografía', 'mapas', 'países', 'continentes', 'política'], true),
        ('economía_y_finanzas', 'Rama especializada en economía y finanzas', ARRAY['economía', 'finanzas', 'mercado', 'inversión', 'presupuesto'], true),
        ('derecho_y_políticas_públicas', 'Rama especializada en derecho y políticas públicas', ARRAY['derecho', 'leyes', 'justicia', 'políticas', 'gobierno'], true),
        ('educación_y_pedagogía', 'Rama especializada en educación y pedagogía', ARRAY['educación', 'enseñanza', 'aprendizaje', 'pedagogía', 'didáctica'], true),
        ('ingeniería', 'Rama especializada en ingeniería', ARRAY['ingeniería', 'diseño', 'construcción', 'tecnología', 'innovación'], true),
        ('empresa_y_emprendimiento', 'Rama especializada en empresa y emprendimiento', ARRAY['empresa', 'negocios', 'emprendimiento', 'gestión', 'liderazgo'], true),
        ('arte_música_y_cultura', 'Rama especializada en arte, música y cultura', ARRAY['arte', 'música', 'cultura', 'creatividad', 'expresión'], true),
        ('literatura_y_escritura', 'Rama especializada en literatura y escritura', ARRAY['literatura', 'escritura', 'novelas', 'poesía', 'redacción'], true),
        ('medios_y_comunicación', 'Rama especializada en medios y comunicación', ARRAY['medios', 'comunicación', 'periodismo', 'audiovisual', 'marketing'], true),
        ('deportes_y_esports', 'Rama especializada en deportes y esports', ARRAY['deportes', 'atletismo', 'competición', 'entrenamiento', 'gaming'], true),
        ('juegos_y_entretenimiento', 'Rama especializada en juegos y entretenimiento', ARRAY['juegos', 'videojuegos', 'entretenimiento', 'diversión', 'gaming'], true),
        ('cocina_y_nutrición', 'Rama especializada en cocina y nutrición', ARRAY['cocina', 'recetas', 'nutrición', 'alimentación', 'gastronomía'], true),
        ('hogar_diy_y_reparaciones', 'Rama especializada en hogar, DIY y reparaciones', ARRAY['hogar', 'bricolaje', 'reparaciones', 'mantenimiento', 'construcción'], true),
        ('viajes_e_idiomas', 'Rama especializada en viajes e idiomas', ARRAY['viajes', 'turismo', 'idiomas', 'culturas', 'aventura'], true),
        ('vida_diaria_legal_práctico_y_trámites', 'Rama especializada en vida diaria, legal, práctico y trámites', ARRAY['vida diaria', 'legal', 'práctico', 'trámites', 'administrativo'], true),
        ('sociología_y_antropología', 'Rama especializada en sociología y antropología', ARRAY['sociología', 'antropología', 'sociedad', 'cultura', 'comportamiento'], true),
        ('neurociencia_y_psicología', 'Rama especializada en neurociencia y psicología', ARRAY['neurociencia', 'psicología', 'mente', 'comportamiento', 'cerebro'], true),
        ('astronomía_y_espacio', 'Rama especializada en astronomía y espacio', ARRAY['astronomía', 'espacio', 'estrellas', 'galaxias', 'cosmos'], true),
        ('ciencias_de_la_tierra_y_clima', 'Rama especializada en ciencias de la tierra y clima', ARRAY['geología', 'clima', 'medio ambiente', 'ecología', 'sostenibilidad'], true),
        ('ciencia_de_datos_e_ia', 'Rama especializada en ciencia de datos e IA', ARRAY['datos', 'inteligencia artificial', 'machine learning', 'estadística', 'análisis'], true),
        ('ciberseguridad_y_criptografía', 'Rama especializada en ciberseguridad y criptografía', ARRAY['seguridad', 'criptografía', 'ciberseguridad', 'privacidad', 'protección'], true),
        ('electrónica_y_iot', 'Rama especializada en electrónica y IoT', ARRAY['electrónica', 'iot', 'dispositivos', 'sensores', 'conectividad'], true),
        ('sistemas_devops_redes', 'Rama especializada en sistemas, DevOps y redes', ARRAY['sistemas', 'devops', 'redes', 'infraestructura', 'automatización'], true),
        ('diseño_y_ux', 'Rama especializada en diseño y UX', ARRAY['diseño', 'ux', 'ui', 'experiencia', 'interfaz'], true),
        ('general', 'Rama general para conversaciones cotidianas', ARRAY['general', 'común', 'básico', 'conversación', 'cotidiano'], true),
        ('maestros_de_los_números', 'Rama especializada en maestros de los números', ARRAY['matemáticas', 'números', 'cálculo', 'estadística', 'álgebra'], true),
        ('sanadores_del_cuerpo_y_alma', 'Rama especializada en sanadores del cuerpo y alma', ARRAY['salud', 'bienestar', 'medicina', 'psicología', 'holístico'], true)
    ON CONFLICT (name)
    DO UPDATE SET
        description = EXCLUDED.description,
        keywords = EXCLUDED.keywords,
        enabled = EXCLUDED.enabled,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;

-- Datos iniciales de ejemplo
DO $$
BEGIN
    -- Registrar modelos de ejemplo
    PERFORM update_model_registry(
        'Sheily-Comprension-Model', 
        'Classification', 
        'Phi-3-mini', 
        'Corpus de Conversaciones en Español', 
        120, 
        50000, 
        500.5, 
        'GPU', 
        '1.0.0', 
        'Modelo de comprensión de texto en español',
        '{"best_accuracy": 0.9, "best_epoch": 10}',
        '{"baseModel": "Phi-3-mini", "quantization": "4bit", "domain": "general"}'
    );

    PERFORM update_model_registry(
        'Sheily-Matematicas-Model', 
        'LoRA', 
        'Phi-3-mini', 
        'Datos de Dominio Específico', 
        90, 
        25000, 
        350.2, 
        'GPU', 
        '1.0.0', 
        'Modelo especializado en matemáticas',
        '{"best_accuracy": 0.82, "best_epoch": 9}',
        '{"baseModel": "Phi-3-mini", "quantization": "4bit", "domain": "mathematics"}'
    );

    -- Insertar métricas de entrenamiento de ejemplo
    PERFORM insert_training_metrics(
        'Sheily-Comprension-Model', 1, 0.5, 1.2, 0.5, 
        0.001, 32, 300.5, 4096, 75.5
    );
    PERFORM insert_training_metrics(
        'Sheily-Comprension-Model', 5, 0.8, 0.5, 0.75, 
        0.0005, 32, 305.2, 4096, 80.2
    );
    PERFORM insert_training_metrics(
        'Sheily-Comprension-Model', 10, 0.9, 0.25, 0.87, 
        0.0001, 32, 310.0, 4096, 85.0
    );

    PERFORM insert_training_metrics(
        'Sheily-Matematicas-Model', 1, 0.4, 1.3, 0.4, 
        0.001, 32, 250.5, 4096, 70.5
    );
    PERFORM insert_training_metrics(
        'Sheily-Matematicas-Model', 5, 0.7, 0.6, 0.68, 
        0.0005, 32, 255.2, 4096, 75.2
    );
    PERFORM insert_training_metrics(
        'Sheily-Matematicas-Model', 9, 0.82, 0.35, 0.78, 
        0.0001, 32, 260.0, 4096, 80.0
    );
END $$;
