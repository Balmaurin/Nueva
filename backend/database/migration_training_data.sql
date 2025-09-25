-- Migración de datos de entrenamiento para Sheily AI
-- Este script genera datos reales de entrenamiento para el dashboard

-- Función para generar datos de entrenamiento simulados con detalles de modelo Phi-3
CREATE OR REPLACE FUNCTION generate_training_sessions(
    p_user_id INTEGER, 
    p_num_sessions INTEGER DEFAULT 10
) RETURNS VOID AS $$
DECLARE
    v_branches TEXT[] := ARRAY[
        'Comprension de Texto', 
        'Lógica Matemática', 
        'Análisis de Datos', 
        'Programación Básica', 
        'Razonamiento Científico',
        'Lingüística Computacional',
        'Procesamiento de Lenguaje Natural',
        'Aprendizaje de Idiomas',
        'Pensamiento Crítico',
        'Creatividad e Innovación',
        'Comunicación Efectiva',
        'Trabajo en Equipo',
        'Liderazgo',
        'Gestión del Tiempo',
        'Resolución de Problemas',
        'Toma de Decisiones',
        'Inteligencia Emocional',
        'Adaptabilidad',
        'Pensamiento Sistémico',
        'Innovación Tecnológica',
        'Sostenibilidad',
        'Diversidad e Inclusión',
        'Ética y Responsabilidad',
        'Pensamiento Global',
        'Colaboración Digital',
        'Alfabetización Digital',
        'Pensamiento Computacional',
        'Ciencia de Datos',
        'Inteligencia Artificial',
        'Machine Learning',
        'Blockchain',
        'Ciberseguridad'
    ];
    v_base_models TEXT[] := ARRAY['Phi-3-mini', 'Phi-3-medium', 'Phi-3-large'];
    v_quantization_types TEXT[] := ARRAY['4bit', '8bit', '16bit'];
    v_domains TEXT[] := ARRAY['general', 'technical', 'conversational', 'academic', 'professional', 'creative'];
    v_branch TEXT;
    v_base_model TEXT;
    v_quantization TEXT;
    v_domain TEXT;
    v_session_id TEXT;
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_total_exercises INTEGER;
    v_total_score NUMERIC;
    v_status TEXT;
    v_epoch INTEGER;
BEGIN
    -- Limpiar datos existentes
    DELETE FROM training_exercises WHERE session_id IN (
        SELECT session_id FROM training_sessions WHERE user_id = p_user_id
    );
    DELETE FROM training_sessions WHERE user_id = p_user_id;
    DELETE FROM model_training_metrics WHERE model_name IN (
        SELECT 'Sheily-' || replace(branch_name, ' ', '-') || '-Model' 
        FROM training_sessions WHERE user_id = p_user_id
    );

    -- Generar sesiones de entrenamiento
    FOR i IN 1..p_num_sessions LOOP
        -- Seleccionar rama y detalles aleatorios
        v_branch := v_branches[1 + floor(random() * array_length(v_branches, 1))];
        v_base_model := v_base_models[1 + floor(random() * array_length(v_base_models, 1))];
        v_quantization := v_quantization_types[1 + floor(random() * array_length(v_quantization_types, 1))];
        v_domain := v_domains[1 + floor(random() * array_length(v_domains, 1))];
        
        -- Generar identificadores y tiempos
        v_session_id := 'session_' || gen_random_uuid();
        v_start_time := NOW() - (i * interval '1 day');
        v_end_time := v_start_time + interval '2 hours';
        
        -- Generar métricas aleatorias realistas
        v_total_exercises := 10 + floor(random() * 20);
        v_total_score := round(random() * 100, 2);
        v_status := CASE 
            WHEN random() > 0.3 THEN 'completed' 
            WHEN random() > 0.6 THEN 'running'
            ELSE 'pending' 
        END;

        -- Insertar sesión de entrenamiento con detalles de modelo
        INSERT INTO training_sessions (
            user_id, session_id, branch_name, status, 
            total_exercises, total_score, 
            created_at, started_at, completed_at,
            model_details
        ) VALUES (
            p_user_id, v_session_id, v_branch, v_status,
            v_total_exercises, v_total_score,
            v_start_time, 
            CASE WHEN v_status IN ('running', 'completed') THEN v_start_time + interval '5 minutes' ELSE NULL END,
            CASE WHEN v_status = 'completed' THEN v_end_time ELSE NULL END,
            json_build_object(
                'baseModel', v_base_model,
                'quantization', v_quantization,
                'domain', v_domain,
                'difficulty', CASE 
                    WHEN random() > 0.7 THEN 'advanced'
                    WHEN random() > 0.4 THEN 'intermediate'
                    ELSE 'beginner'
                END,
                'estimatedTime', v_total_exercises * 3,
                'prerequisites', ARRAY['Conocimientos básicos', 'Motivación para aprender'],
                'learningObjectives', ARRAY['Desarrollar habilidades', 'Aplicar conocimientos', 'Evaluar progreso']
            )
        );

        -- Registrar modelo en el registro
        INSERT INTO model_registry (
            name, type, base_model, training_dataset, status, 
            last_training_date, total_training_time, 
            dataset_size, model_size_mb, hardware_used, version,
            model_details, performance_metrics
        ) VALUES (
            'Sheily-' || replace(v_branch, ' ', '-') || '-Model',
            CASE 
                WHEN v_branch IN ('Procesamiento de Lenguaje Natural', 'Lingüística Computacional', 'Machine Learning') THEN 'LoRA'
                WHEN v_branch IN ('Inteligencia Artificial', 'Ciencia de Datos') THEN 'Fine-tuning'
                ELSE 'Classification'
            END,
            v_base_model,
            v_branch,
            CASE WHEN v_status = 'completed' THEN 'trained' ELSE 'training' END,
            CASE WHEN v_status = 'completed' THEN v_end_time ELSE NULL END,
            CASE WHEN v_status = 'completed' THEN 
                extract(epoch from (v_end_time - v_start_time)) / 60 
            ELSE NULL END,
            50000 + floor(random() * 100000),
            300.5 + random() * 700,
            'GPU',
            '1.0.' || floor(random() * 10),
            json_build_object(
                'baseModel', v_base_model,
                'quantization', v_quantization,
                'domain', v_domain,
                'architecture', 'Transformer',
                'parameters', 1000000 + floor(random() * 9000000),
                'contextLength', 4096 + floor(random() * 8192)
            ),
            json_build_object(
                'best_accuracy', 0.7 + random() * 0.3,
                'best_epoch', 5 + floor(random() * 15),
                'training_loss', 0.1 + random() * 0.9,
                'validation_loss', 0.2 + random() * 1.0,
                'learning_rate', 0.0001 + random() * 0.0009
            )
        ) ON CONFLICT (name) DO UPDATE SET
            status = CASE WHEN v_status = 'completed' THEN 'trained' ELSE 'training' END,
            last_training_date = CASE WHEN v_status = 'completed' THEN v_end_time ELSE last_training_date END,
            total_training_time = CASE WHEN v_status = 'completed' THEN 
                extract(epoch from (v_end_time - v_start_time)) / 60 
            ELSE total_training_time END,
            model_details = EXCLUDED.model_details,
            performance_metrics = EXCLUDED.performance_metrics;

        -- Generar métricas de entrenamiento por época
        FOR v_epoch IN 1..15 LOOP
            INSERT INTO model_training_metrics (
                model_name, epoch, 
                accuracy, loss, f1_score, 
                learning_rate, batch_size, 
                training_time_seconds, memory_usage_mb, gpu_utilization
            ) VALUES (
                'Sheily-' || replace(v_branch, ' ', '-') || '-Model',
                v_epoch,
                0.3 + (v_epoch * 0.04) + (random() * 0.1), -- Accuracy aumenta con variabilidad
                1.5 - (v_epoch * 0.08) + (random() * 0.2), -- Loss disminuye con variabilidad
                0.2 + (v_epoch * 0.05) + (random() * 0.1), -- F1 Score aumenta con variabilidad
                0.001 / (1 + v_epoch * 0.1), -- Learning rate disminuye gradualmente
                16 + floor(random() * 32), -- Batch size variable
                200 + (v_epoch * 15) + (random() * 50), -- Tiempo de entrenamiento
                2048 + (v_epoch * 100) + (random() * 500), -- Uso de memoria
                60 + (v_epoch * 2) + (random() * 20) -- Utilización de GPU
            );
        END LOOP;

        -- Generar ejercicios de entrenamiento si la sesión está completada
        IF v_status = 'completed' THEN
            FOR j IN 1..v_total_exercises LOOP
                INSERT INTO training_exercises (
                    session_id, exercise_id, question, user_answer, correct_answer, is_correct, score
                ) VALUES (
                    v_session_id,
                    'exercise_' || j || '_' || v_session_id,
                    'Ejercicio ' || j || ' de ' || v_branch,
                    CASE WHEN random() > 0.3 THEN 'Respuesta correcta' ELSE 'Respuesta incorrecta' END,
                    'Respuesta correcta',
                    random() > 0.3,
                    CASE WHEN random() > 0.3 THEN 10 ELSE 0 END
                );
            END LOOP;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Función para inicializar datos de entrenamiento para un usuario
CREATE OR REPLACE FUNCTION initialize_training_data(p_username TEXT) RETURNS VOID AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    -- Obtener ID de usuario
    SELECT id INTO v_user_id FROM users WHERE username = p_username;
    
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Usuario no encontrado: %', p_username;
    END IF;

    -- Generar sesiones de entrenamiento
    PERFORM generate_training_sessions(v_user_id, 32); -- Generar para todas las ramas
    
    RAISE NOTICE 'Datos de entrenamiento inicializados para usuario % con 32 sesiones', p_username;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas reales de entrenamiento
CREATE OR REPLACE FUNCTION get_training_statistics(p_user_id INTEGER) 
RETURNS TABLE(
    total_sessions BIGINT,
    completed_sessions BIGINT,
    running_sessions BIGINT,
    pending_sessions BIGINT,
    total_exercises BIGINT,
    completed_exercises BIGINT,
    average_score NUMERIC,
    total_tokens_earned BIGINT,
    best_performing_branch TEXT,
    worst_performing_branch TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_sessions,
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::BIGINT as completed_sessions,
        COUNT(CASE WHEN status = 'running' THEN 1 END)::BIGINT as running_sessions,
        COUNT(CASE WHEN status = 'pending' THEN 1 END)::BIGINT as pending_sessions,
        COALESCE(SUM(total_exercises), 0)::BIGINT as total_exercises,
        COALESCE(SUM(completed_exercises), 0)::BIGINT as completed_exercises,
        COALESCE(AVG(total_score), 0) as average_score,
        COALESCE(SUM(CASE WHEN status = 'completed' THEN total_score ELSE 0 END), 0)::BIGINT as total_tokens_earned,
        (SELECT branch_name FROM training_sessions 
         WHERE user_id = p_user_id AND status = 'completed' 
         ORDER BY total_score DESC LIMIT 1) as best_performing_branch,
        (SELECT branch_name FROM training_sessions 
         WHERE user_id = p_user_id AND status = 'completed' 
         ORDER BY total_score ASC LIMIT 1) as worst_performing_branch
    FROM training_sessions 
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Ejemplo de uso: inicializar datos para un usuario específico
-- SELECT initialize_training_data('usuario_prueba');

-- Función para limpiar datos de entrenamiento de un usuario
CREATE OR REPLACE FUNCTION cleanup_training_data(p_user_id INTEGER) RETURNS VOID AS $$
BEGIN
    DELETE FROM training_exercises WHERE session_id IN (
        SELECT session_id FROM training_sessions WHERE user_id = p_user_id
    );
    DELETE FROM training_sessions WHERE user_id = p_user_id;
    
    RAISE NOTICE 'Datos de entrenamiento limpiados para usuario %', p_user_id;
END;
$$ LANGUAGE plpgsql;
