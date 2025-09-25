import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
from dataclasses import dataclass
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


@dataclass
class EnhancedExercise:
    """Estructura de un ejercicio mejorado con 10 preguntas"""

    id: str
    branch: str
    micro_branch: str
    exercise_type: str
    title: str
    description: str
    difficulty: str  # 'básico', 'intermedio', 'avanzado'
    content: str
    solution: str
    hints: List[str]
    tags: List[str]
    created_date: datetime
    estimated_time: int  # minutos
    points: int
    questions: List[Dict[str, Any]]  # 10 preguntas por ejercicio


class EnhancedDailyExerciseGenerator:
    """
    Generador mejorado de ejercicios diarios: 10 ejercicios por micro-rama, cada uno con 10 preguntas
    """

    def __init__(self, branches_path: str = "shaili_ai/branches"):
        self.logger = logging.getLogger(__name__)
        self.branches_path = Path(branches_path)
        self.scheduler = AsyncIOScheduler()

        # Configuración de dificultad por día de la semana
        self.difficulty_schedule = {
            0: "básico",  # Lunes
            1: "básico",  # Martes
            2: "intermedio",  # Miércoles
            3: "intermedio",  # Jueves
            4: "avanzado",  # Viernes
            5: "avanzado",  # Sábado
            6: "básico",  # Domingo
        }

        # Plantillas de ejercicios por rama con micro-ramas
        self.exercise_templates = self._load_exercise_templates()

        # Historial de ejercicios generados
        self.exercise_history: Dict[str, List[str]] = {}

    def _load_exercise_templates(self) -> Dict[str, Dict[str, Any]]:
        """Cargar plantillas de ejercicios por rama con micro-ramas"""
        templates = {}

        # 1. LENGUA Y LINGÜÍSTICA
        templates["lengua_y_lingüística"] = {
            "micro_ramas": {
                "gramática": {
                    "tema": "Análisis gramatical de oraciones",
                    "tipos_ejercicios": [
                        "análisis_morfosintáctico",
                        "identificación_categorías",
                        "análisis_funciones",
                        "clasificación_oraciones",
                        "análisis_complejo",
                        "identificación_elementos",
                        "análisis_estructura",
                        "clasificación_tipos",
                        "análisis_detallado",
                        "ejercicio_integral",
                    ],
                },
                "sintaxis": {
                    "tema": "Análisis sintáctico de estructuras",
                    "tipos_ejercicios": [
                        "análisis_sintáctico_básico",
                        "identificación_sujeto_predicado",
                        "análisis_complementos",
                        "estructura_oracional",
                        "análisis_complejo",
                        "identificación_funciones",
                        "análisis_árbol_sintáctico",
                        "clasificación_oraciones",
                        "análisis_detallado",
                        "ejercicio_integral",
                    ],
                },
            }
        }

        # 2. MATEMÁTICAS
        templates["matemáticas"] = {
            "micro_ramas": {
                "álgebra": {
                    "tema": "Resolución de ecuaciones algebraicas",
                    "tipos_ejercicios": [
                        "ecuaciones_lineales",
                        "ecuaciones_cuadráticas",
                        "sistemas_ecuaciones",
                        "polinomios",
                        "factorización",
                        "ecuaciones_racionales",
                        "ecuaciones_irracionales",
                        "ecuaciones_exponenciales",
                        "ecuaciones_logarítmicas",
                        "problemas_aplicados",
                    ],
                },
                "cálculo": {
                    "tema": "Cálculo diferencial e integral",
                    "tipos_ejercicios": [
                        "derivadas_básicas",
                        "regla_cadena",
                        "derivadas_implícitas",
                        "aplicaciones_derivadas",
                        "integrales_básicas",
                        "integración_por_partes",
                        "integrales_trigonométricas",
                        "series_taylor",
                        "límites",
                        "problemas_aplicados",
                    ],
                },
            }
        }

        # 3. COMPUTACIÓN Y PROGRAMACIÓN
        templates["computación_y_programación"] = {
            "micro_ramas": {
                "algoritmos": {
                    "tema": "Implementación y análisis de algoritmos",
                    "tipos_ejercicios": [
                        "algoritmos_búsqueda",
                        "algoritmos_ordenamiento",
                        "algoritmos_recursivos",
                        "análisis_complejidad",
                        "algoritmos_grafos",
                        "programación_dinámica",
                        "algoritmos_divide_conquista",
                        "algoritmos_avaros",
                        "algoritmos_backtracking",
                        "optimización_algoritmos",
                    ],
                },
                "estructuras_datos": {
                    "tema": "Implementación y uso de estructuras de datos",
                    "tipos_ejercicios": [
                        "arrays_listas",
                        "pilas_colas",
                        "árboles_binarios",
                        "árboles_búsqueda",
                        "grafos",
                        "tablas_hash",
                        "montículos",
                        "árboles_avl",
                        "estructuras_avanzadas",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 4. CIENCIA DE DATOS E IA
        templates["ciencia_de_datos_e_ia"] = {
            "micro_ramas": {
                "modelado": {
                    "tema": "Construcción y evaluación de modelos de machine learning",
                    "tipos_ejercicios": [
                        "regresión_lineal",
                        "clasificación_binaria",
                        "clasificación_multiclase",
                        "regresión_logística",
                        "árboles_decisión",
                        "random_forest",
                        "support_vector_machines",
                        "redes_neuronales",
                        "deep_learning",
                        "ensemble_methods",
                    ],
                },
                "preprocesamiento": {
                    "tema": "Preparación y limpieza de datos",
                    "tipos_ejercicios": [
                        "limpieza_datos",
                        "manejo_valores_faltantes",
                        "normalización_estandarización",
                        "codificación_variables",
                        "selección_características",
                        "reducción_dimensionalidad",
                        "balanceo_datos",
                        "detección_outliers",
                        "transformación_datos",
                        "pipeline_preprocesamiento",
                    ],
                },
            }
        }

        # 5. FÍSICA
        templates["física"] = {
            "micro_ramas": {
                "mecánica": {
                    "tema": "Problemas de mecánica clásica",
                    "tipos_ejercicios": [
                        "cinemática_rectilínea",
                        "cinemática_circular",
                        "dinámica_newtoniana",
                        "trabajo_energía",
                        "conservación_energía",
                        "cantidad_movimiento",
                        "colisiones",
                        "movimiento_armónico",
                        "mecánica_fluidos",
                        "problemas_aplicados",
                    ],
                },
                "electromagnetismo": {
                    "tema": "Problemas de electromagnetismo",
                    "tipos_ejercicios": [
                        "campos_eléctricos",
                        "potencial_eléctrico",
                        "corriente_resistencia",
                        "circuitos_dc",
                        "campos_magnéticos",
                        "inducción_electromagnética",
                        "ondas_electromagnéticas",
                        "circuitos_ac",
                        "electromagnetismo_avanzado",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 6. QUÍMICA
        templates["química"] = {
            "micro_ramas": {
                "química_orgánica": {
                    "tema": "Síntesis y reacciones de compuestos orgánicos",
                    "tipos_ejercicios": [
                        "nomenclatura_orgánica",
                        "reacciones_sustitución",
                        "reacciones_eliminación",
                        "reacciones_adición",
                        "oxidación_reducción",
                        "síntesis_compuestos",
                        "mecanismos_reacción",
                        "estereoquímica",
                        "espectroscopía",
                        "aplicaciones_industriales",
                    ],
                },
                "bioquímica": {
                    "tema": "Procesos bioquímicos y biomoléculas",
                    "tipos_ejercicios": [
                        "aminoácidos_proteínas",
                        "carbohidratos",
                        "lípidos",
                        "enzimas_catálisis",
                        "metabolismo_energético",
                        "ácidos_nucleicos",
                        "regulación_metabólica",
                        "señalización_celular",
                        "bioquímica_clínica",
                        "aplicaciones_biomédicas",
                    ],
                },
            }
        }

        # 7. BIOLOGÍA
        templates["biología"] = {
            "micro_ramas": {
                "genética": {
                    "tema": "Herencia genética y análisis de genes",
                    "tipos_ejercicios": [
                        "herencia_mendeliana",
                        "cuadros_punnett",
                        "herencia_linked",
                        "mutaciones_genéticas",
                        "genética_poblaciones",
                        "mapeo_genes",
                        "genética_molecular",
                        "genómica",
                        "genética_evolutiva",
                        "aplicaciones_biomédicas",
                    ],
                },
                "ecología": {
                    "tema": "Interacciones ecológicas y dinámica de poblaciones",
                    "tipos_ejercicios": [
                        "dinámica_poblaciones",
                        "interacciones_especies",
                        "sucesión_ecológica",
                        "ciclos_biogeoquímicos",
                        "biodiversidad",
                        "conservación_especies",
                        "ecología_comunidades",
                        "ecosistemas",
                        "cambio_climático",
                        "sostenibilidad",
                    ],
                },
            }
        }

        # 8. MEDICINA Y SALUD
        templates["medicina_y_salud"] = {
            "micro_ramas": {
                "diagnóstico": {
                    "tema": "Diagnóstico clínico y análisis de casos",
                    "tipos_ejercicios": [
                        "anamnesis_exploración",
                        "diagnóstico_diferencial",
                        "interpretación_pruebas",
                        "casos_clínicos",
                        "algoritmos_diagnóstico",
                        "medicina_emergencias",
                        "diagnóstico_imagen",
                        "laboratorio_clínico",
                        "diagnóstico_molecular",
                        "medicina_personalizada",
                    ],
                },
                "farmacología": {
                    "tema": "Farmacología clínica y terapéutica",
                    "tipos_ejercicios": [
                        "farmacocinética",
                        "farmacodinamia",
                        "interacciones_farmacológicas",
                        "efectos_adversos",
                        "dosificación_medicamentos",
                        "farmacología_clínica",
                        "terapéutica_específica",
                        "monitoreo_farmacológico",
                        "farmacogenética",
                        "medicina_personalizada",
                    ],
                },
            }
        }

        # 9. NEUROCIENCIA Y PSICOLOGÍA
        templates["neurociencia_y_psicología"] = {
            "micro_ramas": {
                "psicología_cognitiva": {
                    "tema": "Procesos cognitivos y funcionamiento mental",
                    "tipos_ejercicios": [
                        "atención_percepción",
                        "memoria_aprendizaje",
                        "lenguaje_comunicación",
                        "razonamiento_resolución",
                        "toma_decisiones",
                        "inteligencia_creatividad",
                        "desarrollo_cognitivo",
                        "neuropsicología",
                        "cognición_social",
                        "aplicaciones_clínicas",
                    ],
                },
                "neurofisiología": {
                    "tema": "Funcionamiento del sistema nervioso",
                    "tipos_ejercicios": [
                        "potenciales_membrana",
                        "transmisión_sináptica",
                        "neurotransmisores",
                        "vías_neurales",
                        "plasticidad_sináptica",
                        "sistemas_sensoriales",
                        "control_motor",
                        "sistemas_autónomos",
                        "neuroendocrinología",
                        "neuropatología",
                    ],
                },
            }
        }

        # 10. INGENIERÍA
        templates["ingeniería"] = {
            "micro_ramas": {
                "ingeniería_eléctrica": {
                    "tema": "Diseño y análisis de circuitos eléctricos",
                    "tipos_ejercicios": [
                        "análisis_circuitos_dc",
                        "análisis_circuitos_ac",
                        "amplificadores_operacionales",
                        "filtros_electrónicos",
                        "fuentes_alimentación",
                        "control_automático",
                        "máquinas_eléctricas",
                        "sistemas_potencia",
                        "electrónica_digital",
                        "aplicaciones_industriales",
                    ],
                },
                "ingeniería_mecánica": {
                    "tema": "Diseño y análisis de sistemas mecánicos",
                    "tipos_ejercicios": [
                        "análisis_estático",
                        "análisis_dinámico",
                        "vibraciones_mecánicas",
                        "diseño_elementos",
                        "mecánica_fluidos",
                        "termodinámica_aplicada",
                        "mecánica_materiales",
                        "control_mecánico",
                        "robótica",
                        "aplicaciones_industriales",
                    ],
                },
            }
        }

        # 11. ELECTRÓNICA Y IOT
        templates["electrónica_y_iot"] = {
            "micro_ramas": {
                "microcontroladores": {
                    "tema": "Programación y aplicación de microcontroladores",
                    "tipos_ejercicios": [
                        "programación_básica",
                        "entradas_salidas",
                        "comunicación_serial",
                        "interrupciones",
                        "timers_pwm",
                        "sensores_actuadores",
                        "comunicación_wireless",
                        "interfaz_usuario",
                        "sistemas_embebidos",
                        "aplicaciones_iot",
                    ],
                },
                "iot": {
                    "tema": "Sistemas de Internet de las Cosas",
                    "tipos_ejercicios": [
                        "arquitectura_iot",
                        "protocolos_comunicación",
                        "sensores_actuadores",
                        "gateways_iot",
                        "cloud_computing",
                        "seguridad_iot",
                        "análisis_datos",
                        "machine_learning_iot",
                        "aplicaciones_smart_city",
                        "sistemas_autónomos",
                    ],
                },
            }
        }

        # 12. CIBERSEGURIDAD Y CRIPTOGRAFÍA
        templates["ciberseguridad_y_criptografía"] = {
            "micro_ramas": {
                "criptografía": {
                    "tema": "Algoritmos criptográficos y seguridad",
                    "tipos_ejercicios": [
                        "criptografía_simétrica",
                        "criptografía_asimétrica",
                        "funciones_hash",
                        "firmas_digitales",
                        "protocolos_seguridad",
                        "criptoanálisis",
                        "cryptocurrencies",
                        "post_quantum_crypto",
                        "homomorphic_encryption",
                        "aplicaciones_prácticas",
                    ],
                },
                "pentesting": {
                    "tema": "Evaluación de vulnerabilidades y testing de penetración",
                    "tipos_ejercicios": [
                        "reconocimiento_información",
                        "análisis_vulnerabilidades",
                        "exploit_development",
                        "post_exploitation",
                        "web_application_testing",
                        "network_penetration",
                        "social_engineering",
                        "wireless_security",
                        "mobile_security",
                        "reporting_remediation",
                    ],
                },
            }
        }

        # 13. SISTEMAS/DEVOPS/REDES
        templates["sistemas_devops_redes"] = {
            "micro_ramas": {
                "devops": {
                    "tema": "Integración y despliegue continuo",
                    "tipos_ejercicios": [
                        "version_control_git",
                        "continuous_integration",
                        "continuous_deployment",
                        "containerization_docker",
                        "orchestration_kubernetes",
                        "infrastructure_as_code",
                        "monitoring_logging",
                        "security_devops",
                        "microservices",
                        "cloud_native_applications",
                    ],
                },
                "redes": {
                    "tema": "Diseño y administración de redes",
                    "tipos_ejercicios": [
                        "protocolos_red",
                        "routing_switching",
                        "network_security",
                        "wireless_networks",
                        "network_monitoring",
                        "quality_of_service",
                        "network_virtualization",
                        "software_defined_networking",
                        "network_automation",
                        "cloud_networking",
                    ],
                },
            }
        }

        # 14. CIENCIAS DE LA TIERRA Y CLIMA
        templates["ciencias_de_la_tierra_y_clima"] = {
            "micro_ramas": {
                "meteorología": {
                    "tema": "Análisis de fenómenos meteorológicos",
                    "tipos_ejercicios": [
                        "análisis_atmosférico",
                        "predicción_clima",
                        "fenómenos_extremos",
                        "modelos_numericos",
                        "observación_remota",
                        "climatología",
                        "meteorología_sinóptica",
                        "meteorología_dinámica",
                        "meteorología_aeronáutica",
                        "aplicaciones_prácticas",
                    ],
                },
                "geología": {
                    "tema": "Análisis geológico y procesos terrestres",
                    "tipos_ejercicios": [
                        "mineralogía_petrología",
                        "estratigrafía",
                        "tectónica_placas",
                        "geología_estructural",
                        "geología_económica",
                        "geología_ambiental",
                        "geología_histórica",
                        "geofísica",
                        "geología_planetaria",
                        "aplicaciones_industriales",
                    ],
                },
            }
        }

        # 15. ASTRONOMÍA Y ESPACIO
        templates["astronomía_y_espacio"] = {
            "micro_ramas": {
                "astrofísica": {
                    "tema": "Física de objetos astronómicos",
                    "tipos_ejercicios": [
                        "física_estelar",
                        "evolución_estelar",
                        "física_galáctica",
                        "cosmología",
                        "materia_oscura",
                        "agujeros_negros",
                        "exoplanetas",
                        "astrofísica_observacional",
                        "astrofísica_computacional",
                        "aplicaciones_tecnológicas",
                    ],
                },
                "mecánica_celeste": {
                    "tema": "Movimiento y dinámica de cuerpos celestes",
                    "tipos_ejercicios": [
                        "órbitas_keplerianas",
                        "perturbaciones_orbitales",
                        "mecánica_planetaria",
                        "navegación_espacial",
                        "satélites_artificiales",
                        "misiones_espaciales",
                        "mecánica_lunar",
                        "mecánica_asteroides",
                        "mecánica_cometas",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 16. ECONOMÍA Y FINANZAS
        templates["economía_y_finanzas"] = {
            "micro_ramas": {
                "microeconomía": {
                    "tema": "Análisis microeconómico de mercados",
                    "tipos_ejercicios": [
                        "oferta_demanda",
                        "elasticidad",
                        "teoría_consumidor",
                        "teoría_productor",
                        "estructuras_mercado",
                        "fallos_mercado",
                        "economía_laboral",
                        "economía_pública",
                        "economía_internacional",
                        "aplicaciones_prácticas",
                    ],
                },
                "finanzas_corporativas": {
                    "tema": "Análisis financiero empresarial",
                    "tipos_ejercicios": [
                        "valoración_empresas",
                        "análisis_estados_financieros",
                        "presupuesto_capital",
                        "estructura_capital",
                        "política_dividendos",
                        "gestión_riesgo",
                        "fusiones_adquisiciones",
                        "finanzas_internacionales",
                        "finanzas_conductuales",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 17. EMPRESA Y EMPRENDIMIENTO
        templates["empresa_y_emprendimiento"] = {
            "micro_ramas": {
                "estrategia": {
                    "tema": "Estrategia empresarial y competitiva",
                    "tipos_ejercicios": [
                        "análisis_competitivo",
                        "formulación_estrategia",
                        "implementación_estrategia",
                        "estrategia_corporativa",
                        "estrategia_business_units",
                        "estrategia_funcional",
                        "innovación_estrategia",
                        "estrategia_digital",
                        "estrategia_internacional",
                        "aplicaciones_prácticas",
                    ],
                },
                "marketing": {
                    "tema": "Estrategias de marketing y comunicación",
                    "tipos_ejercicios": [
                        "análisis_mercado",
                        "segmentación_posicionamiento",
                        "mezcla_marketing",
                        "marketing_digital",
                        "comportamiento_consumidor",
                        "branding",
                        "marketing_relacional",
                        "marketing_internacional",
                        "marketing_analytics",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 18. DERECHO Y POLÍTICAS PÚBLICAS
        templates["derecho_y_políticas_públicas"] = {
            "micro_ramas": {
                "derecho_civil": {
                    "tema": "Análisis de casos de derecho civil",
                    "tipos_ejercicios": [
                        "contratos",
                        "responsabilidad_civil",
                        "derecho_propiedad",
                        "derecho_familia",
                        "sucesiones",
                        "derecho_inmobiliario",
                        "derecho_consumidor",
                        "derecho_laboral",
                        "derecho_comercial",
                        "aplicaciones_prácticas",
                    ],
                },
                "políticas_públicas": {
                    "tema": "Diseño y evaluación de políticas públicas",
                    "tipos_ejercicios": [
                        "análisis_problemas",
                        "formulación_políticas",
                        "implementación_políticas",
                        "evaluación_impacto",
                        "políticas_sociales",
                        "políticas_económicas",
                        "políticas_ambientales",
                        "gobernanza",
                        "participación_ciudadana",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 19. SOCIOLOGÍA Y ANTROPOLOGÍA
        templates["sociología_y_antropología"] = {
            "micro_ramas": {
                "sociología_urbana": {
                    "tema": "Análisis de fenómenos urbanos",
                    "tipos_ejercicios": [
                        "estructura_urbana",
                        "gentrificación",
                        "desigualdad_urbana",
                        "movilidad_urbana",
                        "espacios_públicos",
                        "cultura_urbana",
                        "gobernanza_urbana",
                        "sostenibilidad_urbana",
                        "tecnología_urbana",
                        "aplicaciones_prácticas",
                    ],
                },
                "antropología_cultural": {
                    "tema": "Estudio de culturas y sociedades",
                    "tipos_ejercicios": [
                        "etnografía",
                        "sistemas_culturales",
                        "rituales_ceremonias",
                        "parentesco_familia",
                        "economía_cultural",
                        "política_cultural",
                        "religión_cultura",
                        "cambio_cultural",
                        "antropología_aplicada",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 20. EDUCACIÓN Y PEDAGOGÍA
        templates["educación_y_pedagogía"] = {
            "micro_ramas": {
                "diseño_curricular": {
                    "tema": "Diseño y desarrollo curricular",
                    "tipos_ejercicios": [
                        "análisis_necesidades",
                        "objetivos_aprendizaje",
                        "selección_contenidos",
                        "organización_curricular",
                        "metodologías_enseñanza",
                        "evaluación_aprendizaje",
                        "recursos_educativos",
                        "tecnología_educativa",
                        "curriculum_integrado",
                        "aplicaciones_prácticas",
                    ],
                },
                "metodologías_enseñanza": {
                    "tema": "Estrategias y metodologías pedagógicas",
                    "tipos_ejercicios": [
                        "aprendizaje_activo",
                        "aprendizaje_colaborativo",
                        "aprendizaje_proyectos",
                        "aprendizaje_invertido",
                        "gamificación",
                        "aprendizaje_adaptativo",
                        "evaluación_formativa",
                        "diferenciación_instruccional",
                        "aprendizaje_servicio",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 21. HISTORIA
        templates["historia"] = {
            "micro_ramas": {
                "historia_contemporánea": {
                    "tema": "Análisis de eventos históricos contemporáneos",
                    "tipos_ejercicios": [
                        "revolución_industrial",
                        "guerras_mundiales",
                        "guerra_fría",
                        "descolonización",
                        "movimientos_sociales",
                        "globalización",
                        "revolución_digital",
                        "conflictos_contemporáneos",
                        "historia_cultural",
                        "aplicaciones_actuales",
                    ],
                },
                "historia_arte": {
                    "tema": "Análisis de movimientos y obras artísticas",
                    "tipos_ejercicios": [
                        "renacimiento",
                        "barroco",
                        "romanticismo",
                        "impresionismo",
                        "vanguardias",
                        "arte_contemporáneo",
                        "arte_digital",
                        "crítica_arte",
                        "historia_arquitectura",
                        "aplicaciones_actuales",
                    ],
                },
            }
        }

        # 22. GEOGRAFÍA Y GEO-POLÍTICA
        templates["geografía_y_geo_política"] = {
            "micro_ramas": {
                "geopolítica": {
                    "tema": "Análisis geopolítico de conflictos y alianzas",
                    "tipos_ejercicios": [
                        "conflictos_regionales",
                        "recursos_estratégicos",
                        "alianzas_internacionales",
                        "geopolítica_energía",
                        "geopolítica_agua",
                        "geopolítica_tecnología",
                        "geopolítica_clima",
                        "geopolítica_comercio",
                        "geopolítica_seguridad",
                        "aplicaciones_actuales",
                    ],
                },
                "geografía_económica": {
                    "tema": "Análisis de patrones económicos geográficos",
                    "tipos_ejercicios": [
                        "desarrollo_regional",
                        "globalización_económica",
                        "comercio_internacional",
                        "industria_servicios",
                        "recursos_naturales",
                        "infraestructura_transporte",
                        "urbanización_económica",
                        "desarrollo_sostenible",
                        "geografía_financiera",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 23. ARTE, MÚSICA Y CULTURA
        templates["arte_música_y_cultura"] = {
            "micro_ramas": {
                "composición_musical": {
                    "tema": "Composición y teoría musical",
                    "tipos_ejercicios": [
                        "teoría_armonía",
                        "contrapunto",
                        "análisis_musical",
                        "composición_melodía",
                        "orquestación",
                        "música_electrónica",
                        "composición_coral",
                        "música_cámara",
                        "composición_cinematográfica",
                        "aplicaciones_prácticas",
                    ],
                },
                "análisis_artístico": {
                    "tema": "Análisis crítico de obras artísticas",
                    "tipos_ejercicios": [
                        "elementos_formales",
                        "composición_visual",
                        "análisis_iconográfico",
                        "contexto_histórico",
                        "análisis_estilístico",
                        "crítica_arte",
                        "arte_contemporáneo",
                        "arte_digital",
                        "arte_performance",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 24. LITERATURA Y ESCRITURA
        templates["literatura_y_escritura"] = {
            "micro_ramas": {
                "análisis_literario": {
                    "tema": "Análisis crítico de textos literarios",
                    "tipos_ejercicios": [
                        "análisis_narrativo",
                        "análisis_poético",
                        "análisis_dramático",
                        "crítica_literaria",
                        "teoría_literaria",
                        "análisis_estilístico",
                        "análisis_temático",
                        "análisis_contextual",
                        "análisis_comparativo",
                        "aplicaciones_prácticas",
                    ],
                },
                "creación_literaria": {
                    "tema": "Técnicas de creación literaria",
                    "tipos_ejercicios": [
                        "narrativa_corta",
                        "poesía_creativa",
                        "dramaturgia",
                        "ensayo_literario",
                        "escritura_creativa",
                        "edición_textos",
                        "escritura_periodística",
                        "escritura_académica",
                        "escritura_digital",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 25. MEDIOS Y COMUNICACIÓN
        templates["medios_y_comunicación"] = {
            "micro_ramas": {
                "periodismo": {
                    "tema": "Práctica periodística y comunicación",
                    "tipos_ejercicios": [
                        "reportaje_investigativo",
                        "periodismo_digital",
                        "periodismo_televisión",
                        "periodismo_radio",
                        "fotoperiodismo",
                        "periodismo_deportivo",
                        "periodismo_económico",
                        "periodismo_ciencia",
                        "periodismo_opinion",
                        "aplicaciones_prácticas",
                    ],
                },
                "comunicación_digital": {
                    "tema": "Estrategias de comunicación digital",
                    "tipos_ejercicios": [
                        "redes_sociales",
                        "marketing_digital",
                        "content_marketing",
                        "email_marketing",
                        "seo_sem",
                        "analytics_digital",
                        "comunicación_crisis",
                        "influencer_marketing",
                        "comunicación_corporativa",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 26. DISEÑO Y UX
        templates["diseño_y_ux"] = {
            "micro_ramas": {
                "ux_ui": {
                    "tema": "Diseño de experiencia de usuario",
                    "tipos_ejercicios": [
                        "research_usuarios",
                        "arquitectura_información",
                        "wireframing_prototyping",
                        "diseño_interfaz",
                        "usabilidad_testing",
                        "diseño_responsive",
                        "diseño_accesibilidad",
                        "diseño_emotivo",
                        "diseño_sistemas",
                        "aplicaciones_prácticas",
                    ],
                },
                "diseño_gráfico": {
                    "tema": "Comunicación visual y diseño gráfico",
                    "tipos_ejercicios": [
                        "tipografía",
                        "composición_visual",
                        "branding_identidad",
                        "diseño_editorial",
                        "diseño_publicitario",
                        "diseño_packaging",
                        "ilustración_digital",
                        "diseño_motion",
                        "diseño_3d",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 27. DEPORTES Y ESPORTS
        templates["deportes_y_esports"] = {
            "micro_ramas": {
                "análisis_deportivo": {
                    "tema": "Análisis técnico y táctico deportivo",
                    "tipos_ejercicios": [
                        "análisis_técnica",
                        "análisis_táctica",
                        "análisis_rendimiento",
                        "análisis_competitivo",
                        "análisis_estadístico",
                        "análisis_video",
                        "análisis_biomecánico",
                        "análisis_psicológico",
                        "análisis_estrategia",
                        "aplicaciones_prácticas",
                    ],
                },
                "esports": {
                    "tema": "Análisis de deportes electrónicos",
                    "tipos_ejercicios": [
                        "análisis_gameplay",
                        "estrategias_juego",
                        "meta_análisis",
                        "análisis_equipos",
                        "análisis_torneos",
                        "análisis_streaming",
                        "análisis_mercado",
                        "análisis_tecnología",
                        "análisis_comunidad",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 28. JUEGOS Y ENTRETENIMIENTO
        templates["juegos_y_entretenimiento"] = {
            "micro_ramas": {
                "diseño_juegos": {
                    "tema": "Diseño y desarrollo de videojuegos",
                    "tipos_ejercicios": [
                        "game_design",
                        "narrativa_juegos",
                        "mecánicas_juego",
                        "level_design",
                        "programación_juegos",
                        "arte_juegos",
                        "audio_juegos",
                        "testing_juegos",
                        "monetización",
                        "aplicaciones_prácticas",
                    ],
                },
                "narrativa_interactiva": {
                    "tema": "Creación de narrativas interactivas",
                    "tipos_ejercicios": [
                        "storytelling_interactivo",
                        "ramificaciones_narrativas",
                        "personajes_interactivos",
                        "worldbuilding",
                        "diálogos_interactivos",
                        "narrativa_no_lineal",
                        "narrativa_inmersiva",
                        "narrativa_transmedia",
                        "narrativa_ai",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 29. HOGAR, DIY Y REPARACIONES
        templates["hogar_diy_y_reparaciones"] = {
            "micro_ramas": {
                "bricolaje": {
                    "tema": "Proyectos de bricolaje y manualidades",
                    "tipos_ejercicios": [
                        "proyectos_madera",
                        "proyectos_metal",
                        "proyectos_plástico",
                        "proyectos_textil",
                        "proyectos_electrónicos",
                        "proyectos_jardín",
                        "proyectos_decoración",
                        "proyectos_organización",
                        "proyectos_sostenibles",
                        "aplicaciones_prácticas",
                    ],
                },
                "reparaciones_hogar": {
                    "tema": "Mantenimiento y reparaciones domésticas",
                    "tipos_ejercicios": [
                        "reparaciones_eléctricas",
                        "reparaciones_fontanería",
                        "reparaciones_carpintería",
                        "reparaciones_pintura",
                        "reparaciones_electrodomésticos",
                        "reparaciones_climatización",
                        "reparaciones_techos",
                        "reparaciones_suelos",
                        "reparaciones_seguridad",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 30. COCINA Y NUTRICIÓN
        templates["cocina_y_nutrición"] = {
            "micro_ramas": {
                "gastronomía": {
                    "tema": "Técnicas culinarias y gastronomía",
                    "tipos_ejercicios": [
                        "técnicas_cocción",
                        "cocina_internacional",
                        "pastelería_repostería",
                        "cocina_molecular",
                        "cocina_vegetariana",
                        "cocina_fusión",
                        "presentación_platos",
                        "cocina_profesional",
                        "cocina_sostenible",
                        "aplicaciones_prácticas",
                    ],
                },
                "nutrición": {
                    "tema": "Nutrición y planificación alimentaria",
                    "tipos_ejercicios": [
                        "análisis_nutricional",
                        "planificación_dietas",
                        "nutrición_deportiva",
                        "nutrición_clínica",
                        "nutrición_pediátrica",
                        "nutrición_geriátrica",
                        "nutrición_preventiva",
                        "nutrición_comunitaria",
                        "nutrición_sostenible",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 31. VIAJES E IDIOMAS
        templates["viajes_e_idiomas"] = {
            "micro_ramas": {
                "planificación_viajes": {
                    "tema": "Planificación y organización de viajes",
                    "tipos_ejercicios": [
                        "investigación_destinos",
                        "planificación_itinerarios",
                        "presupuesto_viajes",
                        "reservas_alojamiento",
                        "transporte_viajes",
                        "seguridad_viajes",
                        "viajes_grupo",
                        "viajes_aventura",
                        "viajes_culturales",
                        "aplicaciones_prácticas",
                    ],
                },
                "idiomas": {
                    "tema": "Aprendizaje y enseñanza de idiomas",
                    "tipos_ejercicios": [
                        "gramática_idiomas",
                        "vocabulario_idiomas",
                        "pronunciación_idiomas",
                        "conversación_idiomas",
                        "comprensión_lectora",
                        "comprensión_auditiva",
                        "escritura_idiomas",
                        "cultura_idiomas",
                        "traducción_interpretación",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        # 32. VIDA DIARIA, LEGAL PRÁCTICO Y TRÁMITES
        templates["vida_diaria_legal_práctico_y_trámites"] = {
            "micro_ramas": {
                "trámites_burocráticos": {
                    "tema": "Gestión de trámites y documentación",
                    "tipos_ejercicios": [
                        "documentación_personal",
                        "trámites_fiscales",
                        "trámites_laborales",
                        "trámites_inmobiliarios",
                        "trámites_vehículos",
                        "trámites_sanitarios",
                        "trámites_educativos",
                        "trámites_comerciales",
                        "trámites_internacionales",
                        "aplicaciones_prácticas",
                    ],
                },
                "derecho_práctico": {
                    "tema": "Asesoría legal práctica",
                    "tipos_ejercicios": [
                        "contratos_personales",
                        "derecho_laboral_práctico",
                        "derecho_consumidor",
                        "derecho_familia_práctico",
                        "derecho_inmobiliario_práctico",
                        "derecho_penal_práctico",
                        "derecho_administrativo",
                        "derecho_comercial_práctico",
                        "derecho_internacional_práctico",
                        "aplicaciones_prácticas",
                    ],
                },
            }
        }

        return templates

    async def generate_enhanced_daily_exercises(
        self,
    ) -> Dict[str, List[EnhancedExercise]]:
        """
        Generar 10 ejercicios por micro-rama, cada uno con 10 preguntas
        """
        exercises_by_branch = {}
        today = datetime.now()
        day_of_week = today.weekday()
        difficulty = self.difficulty_schedule[day_of_week]

        # Obtener ramas activas
        active_branches = self._get_active_branches()

        for branch in active_branches:
            try:
                branch_exercises = await self._generate_branch_enhanced_exercises(
                    branch, difficulty, today
                )
                if branch_exercises:
                    exercises_by_branch[branch] = branch_exercises

            except Exception as e:
                self.logger.error(f"Error generando ejercicios para {branch}: {e}")

        return exercises_by_branch

    async def _generate_branch_enhanced_exercises(
        self, branch: str, difficulty: str, date: datetime
    ) -> List[EnhancedExercise]:
        """Generar 10 ejercicios para una rama específica"""

        # Verificar que no se haya generado ya ejercicios para hoy
        if self._exercises_already_generated(branch, date):
            self.logger.info(f"Ejercicios ya generados para {branch} en {date.date()}")
            return []

        # Obtener plantilla de la rama
        template = self.exercise_templates.get(branch)
        if not template:
            self.logger.warning(f"No hay plantilla para la rama {branch}")
            return []

        exercises = []

        # Generar ejercicios para cada micro-rama
        for micro_branch, micro_branch_data in template["micro_ramas"].items():
            try:
                micro_branch_exercises = await self._generate_micro_branch_exercises(
                    branch, micro_branch, micro_branch_data, difficulty, date
                )
                exercises.extend(micro_branch_exercises)

            except Exception as e:
                self.logger.error(
                    f"Error generando ejercicios para micro-rama {micro_branch}: {e}"
                )

        return exercises

    async def _generate_micro_branch_exercises(
        self,
        branch: str,
        micro_branch: str,
        micro_branch_data: Dict[str, Any],
        difficulty: str,
        date: datetime,
    ) -> List[EnhancedExercise]:
        """Generar 10 ejercicios para una micro-rama específica"""

        exercises = []
        tema = micro_branch_data["tema"]
        tipos_ejercicios = micro_branch_data["tipos_ejercicios"]

        # Generar 10 ejercicios diferentes
        for i, exercise_type in enumerate(tipos_ejercicios):
            try:
                exercise = await self._generate_single_enhanced_exercise(
                    branch, micro_branch, exercise_type, tema, difficulty, date, i + 1
                )
                if exercise:
                    exercises.append(exercise)
                    self._save_enhanced_exercise(exercise)

            except Exception as e:
                self.logger.error(
                    f"Error generando ejercicio {exercise_type} para {micro_branch}: {e}"
                )

        return exercises

    async def _generate_single_enhanced_exercise(
        self,
        branch: str,
        micro_branch: str,
        exercise_type: str,
        tema: str,
        difficulty: str,
        date: datetime,
        exercise_number: int,
    ) -> Optional[EnhancedExercise]:
        """Generar un ejercicio individual con 10 preguntas"""

        # Generar contenido específico para el tipo de ejercicio
        content_data = await self._generate_enhanced_content_data(
            branch, micro_branch, exercise_type, difficulty
        )

        # Generar 10 preguntas para el ejercicio
        questions = await self._generate_exercise_questions(
            branch, micro_branch, exercise_type, difficulty, content_data
        )

        # Crear el ejercicio
        exercise = EnhancedExercise(
            id=self._generate_enhanced_exercise_id(
                branch, micro_branch, date, exercise_number
            ),
            branch=branch,
            micro_branch=micro_branch,
            exercise_type=exercise_type,
            title=f"Ejercicio {exercise_number}: {content_data.get('title', f'{exercise_type}')}",
            description=f"Ejercicio de {tema} - {content_data.get('description', f'Práctica de {exercise_type}')}",
            difficulty=difficulty,
            content=content_data.get(
                "content", f"Ejercicio de práctica en {exercise_type}"
            ),
            solution=content_data.get(
                "solution", f"Solución del ejercicio de {exercise_type}"
            ),
            hints=content_data.get(
                "hints",
                [
                    "Lee cuidadosamente el problema",
                    "Divide el problema en pasos más pequeños",
                ],
            ),
            tags=content_data.get(
                "tags", [branch, micro_branch, exercise_type, difficulty]
            ),
            created_date=date,
            estimated_time=self._estimate_enhanced_time(difficulty, exercise_type),
            points=self._calculate_enhanced_points(difficulty, exercise_type),
            questions=questions,
        )

        return exercise

    async def _generate_exercise_questions(
        self,
        branch: str,
        micro_branch: str,
        exercise_type: str,
        difficulty: str,
        content_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generar 10 preguntas específicas para un ejercicio"""

        questions = []

        # Generar 10 preguntas diferentes
        for i in range(10):
            question_data = await self._generate_single_question(
                branch, micro_branch, exercise_type, difficulty, content_data, i + 1
            )
            questions.append(question_data)

        return questions

    async def _generate_single_question(
        self,
        branch: str,
        micro_branch: str,
        exercise_type: str,
        difficulty: str,
        content_data: Dict[str, Any],
        question_number: int,
    ) -> Dict[str, Any]:
        """Generar una pregunta individual"""

        # Generar contenido específico para la pregunta
        question_content = await self._generate_question_content(
            branch, micro_branch, exercise_type, difficulty, question_number
        )

        return {
            "id": f"q_{question_number}",
            "number": question_number,
            "question": question_content.get("question", f"Pregunta {question_number}"),
            "options": question_content.get("options", []),
            "correct_answer": question_content.get("correct_answer", ""),
            "explanation": question_content.get(
                "explanation", f"Explicación de la pregunta {question_number}"
            ),
            "difficulty": difficulty,
            "points": self._calculate_question_points(difficulty),
            "estimated_time": self._estimate_question_time(difficulty),
        }

    async def _generate_question_content(
        self,
        branch: str,
        micro_branch: str,
        exercise_type: str,
        difficulty: str,
        question_number: int,
    ) -> Dict[str, Any]:
        """Generar contenido específico para una pregunta"""

        # Aquí implementarías la lógica específica para generar contenido de preguntas
        # Por ahora, usamos contenido de ejemplo

        if branch == "matemáticas" and micro_branch == "álgebra":
            if exercise_type == "ecuaciones_lineales":
                equations = {
                    "básico": ["2x + 3 = 7", "x - 5 = 10", "3x + 2 = 8"],
                    "intermedio": ["2x + 3y = 7", "x - 2y = 5", "3x + y = 9"],
                    "avanzado": [
                        "2x + 3y + z = 7",
                        "x - 2y + 3z = 5",
                        "3x + y - 2z = 9",
                    ],
                }

                equation = random.choice(equations[difficulty])
                return {
                    "question": f"Resuelve la ecuación: {equation}",
                    "options": ["x = 2", "x = 3", "x = 4", "x = 5"],
                    "correct_answer": "x = 2",
                    "explanation": f"Para resolver {equation}, aplicamos las propiedades de las ecuaciones lineales.",
                }

        elif branch == "computación_y_programación" and micro_branch == "algoritmos":
            if exercise_type == "algoritmos_búsqueda":
                algorithms = {
                    "básico": ["búsqueda lineal", "búsqueda secuencial"],
                    "intermedio": ["búsqueda binaria", "búsqueda por interpolación"],
                    "avanzado": ["búsqueda en árboles", "búsqueda en grafos"],
                }

                algorithm = random.choice(algorithms[difficulty])
                return {
                    "question": f"¿Cuál es la complejidad temporal del algoritmo de {algorithm}?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "correct_answer": "O(n)" if "lineal" in algorithm else "O(log n)",
                    "explanation": f"El algoritmo de {algorithm} tiene una complejidad temporal específica.",
                }

        # Contenido por defecto
        return {
            "question": f"Pregunta {question_number} sobre {exercise_type}",
            "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
            "correct_answer": "Opción A",
            "explanation": f"Explicación de la pregunta {question_number}",
        }

    async def _generate_enhanced_content_data(
        self, branch: str, micro_branch: str, exercise_type: str, difficulty: str
    ) -> Dict[str, Any]:
        """Generar datos específicos para el contenido del ejercicio mejorado"""

        # Datos específicos por rama, micro-rama y tipo de ejercicio
        content_data = {
            "hints": [
                "Lee cuidadosamente el problema",
                "Divide el problema en pasos más pequeños",
            ],
            "tags": [branch, micro_branch, exercise_type, difficulty],
        }

        # Implementar lógica específica para cada combinación
        # Por ahora, usamos datos de ejemplo

        if branch == "matemáticas" and micro_branch == "álgebra":
            if exercise_type == "ecuaciones_lineales":
                content_data.update(
                    {
                        "title": "Sistema de ecuaciones lineales",
                        "description": "Resuelve el sistema de ecuaciones lineales dado",
                        "content": "Dado el sistema de ecuaciones lineales, encuentra los valores de las variables.",
                        "solution": "Aplicando el método de eliminación o sustitución...",
                    }
                )

        elif branch == "computación_y_programación" and micro_branch == "algoritmos":
            if exercise_type == "algoritmos_búsqueda":
                content_data.update(
                    {
                        "title": "Implementación de algoritmos de búsqueda",
                        "description": "Implementa y analiza algoritmos de búsqueda",
                        "content": "Implementa el algoritmo de búsqueda especificado y analiza su complejidad.",
                        "solution": "```python\ndef busqueda_lineal(arr, target):\n    for i, item in enumerate(arr):\n        if item == target:\n            return i\n    return -1\n```",
                    }
                )

        return content_data

    def _generate_enhanced_exercise_id(
        self, branch: str, micro_branch: str, date: datetime, exercise_number: int
    ) -> str:
        """Generar ID único para ejercicio mejorado"""
        date_str = date.strftime("%Y%m%d")
        hash_input = f"{branch}_{micro_branch}_{date_str}_{exercise_number}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"enhanced_{branch}_{micro_branch}_{date_str}_{exercise_number}_{hash_value}"

    def _estimate_enhanced_time(self, difficulty: str, exercise_type: str) -> int:
        """Estimar tiempo para ejercicio mejorado (10 preguntas)"""
        base_time = {"básico": 5, "intermedio": 8, "avanzado": 12}
        return base_time.get(difficulty, 10) * 10  # 10 preguntas

    def _calculate_enhanced_points(self, difficulty: str, exercise_type: str) -> int:
        """Calcular puntos para ejercicio mejorado (10 preguntas)"""
        base_points = {"básico": 2, "intermedio": 3, "avanzado": 5}
        return base_points.get(difficulty, 3) * 10  # 10 preguntas

    def _calculate_question_points(self, difficulty: str) -> int:
        """Calcular puntos para una pregunta individual"""
        return {"básico": 2, "intermedio": 3, "avanzado": 5}.get(difficulty, 3)

    def _estimate_question_time(self, difficulty: str) -> int:
        """Estimar tiempo para una pregunta individual"""
        return {"básico": 5, "intermedio": 8, "avanzado": 12}.get(difficulty, 10)

    def _exercises_already_generated(self, branch: str, date: datetime) -> bool:
        """Verificar si ya se generaron ejercicios para una rama en una fecha"""
        date_str = date.strftime("%Y-%m-%d")
        history_key = f"{branch}_{date_str}"
        return history_key in self.exercise_history

    def _save_enhanced_exercise(self, exercise: EnhancedExercise):
        """Guardar ejercicio mejorado en archivo JSON"""
        try:
            # Crear directorio si no existe
            output_dir = Path("shaili_ai/data/enhanced_daily_exercises")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Nombre del archivo
            date_str = exercise.created_date.strftime("%Y-%m-%d")
            filename = f"{exercise.branch}_{exercise.micro_branch}_{date_str}_{exercise.exercise_type}.json"
            filepath = output_dir / filename

            # Convertir a diccionario para JSON
            exercise_dict = {
                "id": exercise.id,
                "branch": exercise.branch,
                "micro_branch": exercise.micro_branch,
                "exercise_type": exercise.exercise_type,
                "title": exercise.title,
                "description": exercise.description,
                "difficulty": exercise.difficulty,
                "content": exercise.content,
                "solution": exercise.solution,
                "hints": exercise.hints,
                "tags": exercise.tags,
                "created_date": exercise.created_date.isoformat(),
                "estimated_time": exercise.estimated_time,
                "points": exercise.points,
                "questions": exercise.questions,
            }

            # Guardar en archivo
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(exercise_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Ejercicio mejorado guardado: {filepath}")

        except Exception as e:
            self.logger.error(f"Error guardando ejercicio mejorado: {e}")

    def _get_active_branches(self) -> List[str]:
        """Obtener lista de ramas activas"""
        branches = []
        if self.branches_path.exists():
            for branch_dir in self.branches_path.iterdir():
                if branch_dir.is_dir() and branch_dir.name in self.exercise_templates:
                    branches.append(branch_dir.name)
        return branches

    def start_enhanced_scheduler(self):
        """Iniciar el scheduler para generación automática mejorada"""
        # Programar generación diaria a las 12:00 PM (mediodía)
        self.scheduler.add_job(
            self.generate_enhanced_daily_exercises,
            CronTrigger(hour=12, minute=0),
            id="enhanced_daily_exercise_generation",
            name="Generación diaria mejorada de ejercicios",
        )
        self.scheduler.start()
        self.logger.info("Scheduler de ejercicios mejorados iniciado")

    async def get_today_enhanced_exercises(self) -> Dict[str, List[EnhancedExercise]]:
        """Obtener ejercicios mejorados de hoy"""
        today = datetime.now()
        exercises_by_branch = {}

        # Buscar archivos de ejercicios de hoy
        output_dir = Path("shaili_ai/data/enhanced_daily_exercises")
        if not output_dir.exists():
            return exercises_by_branch

        date_str = today.strftime("%Y-%m-%d")

        for filepath in output_dir.glob(f"*_{date_str}_*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    exercise_data = json.load(f)

                # Recrear objeto EnhancedExercise
                exercise = EnhancedExercise(
                    id=exercise_data["id"],
                    branch=exercise_data["branch"],
                    micro_branch=exercise_data["micro_branch"],
                    exercise_type=exercise_data["exercise_type"],
                    title=exercise_data["title"],
                    description=exercise_data["description"],
                    difficulty=exercise_data["difficulty"],
                    content=exercise_data["content"],
                    solution=exercise_data["solution"],
                    hints=exercise_data["hints"],
                    tags=exercise_data["tags"],
                    created_date=datetime.fromisoformat(exercise_data["created_date"]),
                    estimated_time=exercise_data["estimated_time"],
                    points=exercise_data["points"],
                    questions=exercise_data["questions"],
                )

                branch = exercise.branch
                if branch not in exercises_by_branch:
                    exercises_by_branch[branch] = []
                exercises_by_branch[branch].append(exercise)

            except Exception as e:
                self.logger.error(f"Error cargando ejercicio de {filepath}: {e}")

        return exercises_by_branch
