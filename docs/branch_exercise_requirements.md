# Requisitos funcionales y de seguridad por rama

Este documento formaliza los requisitos del sistema de ejercicios para las 35 ramas especializadas de Sheily AI. Cada rama debe ofrecer actividades evaluables **sin datos ficticios**, con resultados trazables en la base de datos PostgreSQL del proyecto y disponibles desde el dashboard seguro del usuario.

## Requisitos transversales

1. **Tipos de ejercicio obligatorios.** Cada rama debe exponer 20 niveles en tres modalidades: preguntas de **Sí o No**, **Verdadero o Falso** y ejercicios de **Elección múltiple** ("Elige la respuesta correcta").
2. **Registro de respuestas oficiales.** Toda actividad debe contar con su respuesta correcta, explicación verificable y trazas de validación almacenadas en `branch_exercise_answers`.
3. **Generación y evaluación del dataset.** Al superar una serie de ejercicios con al menos 95 % de aciertos, el sistema genera un dataset validado (`user_branch_progress.verification_status = 'verified'`) que habilita el entrenamiento LoRA de la rama correspondiente.
4. **Token economy transparente.** Las recompensas en tokens se registran en `user_branch_progress.tokens_awarded` y se respaldan con transacciones en `vault_transactions` cuando corresponda.
5. **Seguridad de acceso.** Las secciones Tokens, Personal y Wallet del dashboard requieren doble autenticación local (PIN de seis dígitos) antes de consumir cualquier endpoint de ejercicios o recompensas.
6. **Auditoría y trazabilidad.** Cada intento queda registrado en `user_branch_attempts` con sello de tiempo, origen de validación y precisión obtenida.
7. **Validación externa de conocimiento.** Cuando la rama lo requiera, el backend almacena en `verification_source` la referencia al servicio o dataset externo usado para validar la respuesta (por ejemplo, DOI, URL de artículo, repositorio público).

## Matriz de requisitos por rama

| Clave | Nombre | Dominio principal | Requisitos funcionales clave | Requisitos de seguridad y calidad |
| --- | --- | --- | --- | --- |
| branch_01 | Guardianes de la Vida | Biología | Diseñar ejercicios sobre anatomía, fisiología y biodiversidad en 20 niveles; usar estudios revisados por pares como referencia para datasets aprobados. | Controlar acceso a material sensible (datos biológicos) y registrar fuentes en `verification_source`; exigir precisión ≥ 95 % antes de liberar tokens. |
| branch_02 | Tejedores del Universo | Física | Cobertura de mecánica clásica, electromagnetismo y física moderna; incluir experimentos reproducibles en modo sí/no y verdadero/falso. | Validar fórmulas mediante fuentes académicas; firmar datasets con hash SHA-256 para evitar manipulación. |
| branch_03 | Alquimistas Modernos | Química | Evaluar química orgánica, inorgánica y analítica; múltiples niveles deben contemplar balanceo y estequiometría en preguntas de selección múltiple. | Almacenar referencias de seguridad sobre manipulación química y reforzar monitoreo de respuestas para evitar instrucciones peligrosas. |
| branch_04 | Exploradores Cósmicos | Astronomía | Incluir observaciones sobre sistemas solares, galaxias y cosmología; ejercicios deben poder enlazar a catálogos abiertos (p.ej., NASA, ESA). | Verificar imágenes y datos astronómicos con metadatos oficiales; bloquear acceso sin PIN para telemetría de misiones. |
| branch_05 | Cronistas de la Tierra | Geología | Cubrir tectónica, vulcanología y estratigrafía; ejercicios de sí/no deben relacionar eventos geológicos y datación. | Conservar trazas de fuentes geocientíficas y mitigar divulgación de ubicaciones sensibles con anonimización. |
| branch_06 | Defensores del Equilibrio | Ecología | Modelar dinámicas poblacionales, biodiversidad y cambio climático; integrar datasets ambientales para validar respuestas. | Aplicar controles de integridad para datos climáticos y mantener registro de licencias de uso. |
| branch_07 | Cartógrafos de la Mente | Neurociencia | Evaluar neuroanatomía, neurofisiología y neurocomputación en 20 niveles con soporte multimedia opcional. | Proteger datos potencialmente sensibles; exigir confirmación adicional antes de revelar datasets con sujetos humanos. |
| branch_08 | Arquitectos del ADN | Genética | Preguntas sobre herencia mendeliana, genómica y edición genética; ejercicios de elección múltiple deben incluir variantes genéticas reales. | Registrar consentimientos/licencias de datos genéticos y restringir instrucciones de bioingeniería sin supervisión. |
| branch_09 | Narradores de Eras Perdidas | Paleontología | Cubrir registro fósil, periodos geológicos y métodos de datación; niveles avanzados deben relacionar especies con contextos paleoambientales. | Citar bases paleontológicas abiertas y prevenir filtración de ubicaciones de yacimientos protegidos. |
| branch_10 | Navegantes de las Profundidades | Oceanografía | Incluir oceanografía física, química y biológica; ejercicios de sí/no deben validar corrientes y fenómenos marinos. | Controlar acceso a datos de sensores marítimos y mantener registros de calibración. |
| branch_11 | Pioneros de la Cognición Digital | Inteligencia Artificial | Niveles cubren aprendizaje supervisado, RL y ética; ejercicios deben basarse en papers y benchmarks actuales. | Validar código y resultados con repositorios reproducibles; exigir evaluación anti-sesgo antes de otorgar tokens. |
| branch_12 | Centinelas Digitales | Ciberseguridad | Preguntas sobre criptografía, hardening y respuesta a incidentes; los escenarios deben ser auditables. | Requerir MFA en acceso a ejercicios críticos y registrar logs de intentos fallidos. |
| branch_13 | Artesanos del Ciberespacio | Desarrollo web | Incluir frontend, backend y DevOps; ejercicios de selección múltiple deben usar estándares actuales. | Escanear respuestas en busca de credenciales o secretos antes de almacenamiento. |
| branch_14 | Tejedores de Conexiones | Redes | Evaluar protocolos, topologías y seguridad de red; preguntas verdadero/falso deben basarse en RFC vigentes. | Registrar configuraciones de laboratorio y aislar datos de infraestructura real del usuario. |
| branch_15 | Constructores de Nubes Digitales | Computación en la nube | Incluir modelos de servicio, automatización y observabilidad; ejercicios deben incorporar arquitecturas multirregión. | Verificar cumplimiento de normativas (p.ej., GDPR) y cifrar credenciales de acceso demo. |
| branch_16 | Creadores de Autómatas | Robótica | Niveles cubren cinemática, control y percepción; incluir simulaciones en datasets verificados. | Aplicar control de versiones a configuraciones robóticas y restringir instrucciones que impliquen daño físico. |
| branch_17 | Arquitectos de Mundos Imaginarios | Realidad virtual | Preguntas sobre motores gráficos, interacción y accesibilidad; ejercicios deben enlazar a estándares WebXR. | Validar activos digitales contra malware y proteger propiedad intelectual de terceros. |
| branch_18 | Forjadores de Confianza Digital | Seguridad digital | Evaluar identidad, auditoría y compliance; ejercicios sí/no deben tratar controles Zero Trust. | Reforzar cifrado de datos de cumplimiento y firmar digitalmente datasets generados. |
| branch_19 | Artesanos del Algoritmo | Ciencia de datos | Cubrir limpieza, modelado y despliegue; ejercicios de elección múltiple deben usar casos de negocio reales. | Registrar métricas de sesgo y fairness antes de liberar tokens. |
| branch_20 | Custodios del Tiempo | Historia | Incluir cronologías, análisis de fuentes y metodología histórica; preguntas deben citar archivos verificables. | Mantener referencias a archivos/datasets con licencias claras y prevenir manipulaciones revisionistas. |
| branch_21 | Guardianes de la Cultura | Antropología | Evaluar teorías culturales, etnografía y métodos mixtos; ejercicios deben respetar diversidad cultural. | Registrar permisos de uso cultural y restringir difusión de datos sensibles de comunidades. |
| branch_22 | Arquitectos del Conocimiento | Filosofía | Preguntas sobre lógica, ética y epistemología; niveles avanzados deben incluir análisis de textos. | Garantizar citas correctas y proteger la integridad de fuentes mediante hashes. |
| branch_23 | Creadores de Narrativas | Literatura | Cubrir géneros, análisis literario y teoría narrativa; ejercicios de elección múltiple deben referir fragmentos reales. | Verificar derechos de autor y almacenar citas con metadatos de licencia. |
| branch_24 | Embajadores Lingüísticos | Lingüística | Evaluar fonética, sintaxis y sociolingüística; ejercicios sí/no deben cubrir reglas formales contrastables. | Restringir divulgación de corpus privados y documentar licencias de uso. |
| branch_25 | Cronistas del Pensamiento Económico | Economía | Incluir micro, macro y econometría; ejercicios deben basarse en datos de organismos oficiales. | Versionar datasets económicos y mantener evidencia de procedencia. |
| branch_26 | Estrategas del Mercado | Marketing | Tratar análisis de mercado, branding y métricas de rendimiento; ejercicios de verdadero/falso validan KPIs reales. | Cifrar datasets con datos personales y registrar consentimiento cuando aplique. |
| branch_27 | Guardianes de la Salud | Medicina | Preguntas sobre diagnóstico, farmacología y protocolos clínicos; la selección múltiple debe usar guías médicas vigentes. | Aplicar normativas HIPAA/LOPD; anonimizar cualquier dato clínico y registrar revisiones médicas. |
| branch_28 | Arquitectos del Bienestar | Psicología | Evaluar teorías, psicometría y ética profesional; ejercicios deben vincularse a escalas validadas. | Controlar acceso a datos sensibles y registrar supervisión profesional. |
| branch_29 | Custodios del Conocimiento Jurídico | Derecho | Cubrir legislación, jurisprudencia y procedimientos; ejercicios deben citar normas vigentes. | Registrar jurisdicción aplicable y garantizar trazabilidad de citas legales. |
| branch_30 | Diseñadores del Futuro Urbano | Arquitectura | Tratar diseño, urbanismo y sostenibilidad; ejercicios de elección múltiple deben referir normas técnicas. | Verificar licencias de planos y proteger datos de infraestructura crítica. |
| branch_31 | Visionarios de la Energía | Energías renovables | Incluir tecnologías solar, eólica y almacenamiento; ejercicios deben considerar métricas reales de eficiencia. | Monitorizar integridad de datos energéticos y registrar certificaciones técnicas. |
| branch_32 | Custodios de la Tierra Digital | Geo-informática | Evaluar SIG, teledetección y análisis espacial; ejercicios deben enlazar a datasets geoespaciales abiertos. | Gestionar restricciones geográficas y cifrar coordenadas sensibles. |
| branch_33 | Guardianes del Comercio Global | Comercio internacional | Incluir tratados, logística y finanzas internacionales; ejercicios deben usar estadísticas oficiales. | Registrar controles de exportación/importación y asegurar trazabilidad documental. |
| branch_34 | Protectores del Saber Financiero | Finanzas | Cubrir contabilidad, inversión y gestión de riesgos; ejercicios deben basarse en reportes auditados. | Cifrar datos financieros y mantener evidencias de validación externa. |
| branch_35 | Visionarios de la Innovación Social | Innovación social | Evaluar emprendimiento social, impacto y métricas de sostenibilidad; ejercicios deben integrar casos reales. | Documentar consentimiento de organizaciones y monitorear métricas de impacto contra manipulación. |

## Consideraciones de cumplimiento

- Todas las colecciones de ejercicios deben pasar revisiones periódicas (`system_logs`) para asegurar que los datasets se mantienen actualizados.
- Los endpoints CRUD recién expuestos requieren autenticación JWT y autorización basada en roles (`role` en `users`), limitando operaciones de escritura a usuarios con permisos administrativos.
- Las fuentes externas utilizadas para validar respuestas deben conservarse al menos 12 meses para auditoría.
- La generación automática de datasets para entrenamiento LoRA debe registrar la configuración empleada en `model_registry` y enlazarse con los progresos verificados de cada rama.

