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
class Exercise:
    """Estructura de un ejercicio diario"""

    id: str
    branch: str
    micro_branch: str
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


class DailyExerciseGenerator:
    """
    Generador de ejercicios diarios específicos por micro-rama
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

    async def generate_daily_exercises(self) -> Dict[str, Exercise]:
        """
        Generar ejercicios diarios para todas las ramas activas
        """
        exercises = {}
        today = datetime.now()
        day_of_week = today.weekday()
        difficulty = self.difficulty_schedule[day_of_week]

        # Obtener ramas activas
        active_branches = self._get_active_branches()

        for branch in active_branches:
            try:
                exercise = await self._generate_branch_exercise(
                    branch, difficulty, today
                )
                if exercise:
                    exercises[branch] = exercise
                    self._save_exercise(exercise)

            except Exception as e:
                self.logger.error(f"Error generando ejercicio para {branch}: {e}")

        return exercises

    async def _generate_branch_exercise(
        self, branch: str, difficulty: str, date: datetime
    ) -> Optional[Exercise]:
        """Generar ejercicio específico para una rama"""

        # Verificar que no se haya generado ya un ejercicio para hoy
        if self._exercise_already_generated(branch, date):
            self.logger.info(f"Ejercicio ya generado para {branch} en {date.date()}")
            return None

        # Obtener plantilla de la rama
        template = self.exercise_templates.get(branch)
        if not template:
            self.logger.warning(f"No hay plantilla para la rama {branch}")
            return None

        # Seleccionar tipo de ejercicio
        exercise_type = random.choice(template["tipos"])
        format_template = template["formats"].get(exercise_type, {})

        # Generar contenido específico
        content_data = await self._generate_content_data(
            branch, exercise_type, difficulty
        )

        # Crear ejercicio
        exercise = Exercise(
            id=self._generate_exercise_id(branch, date),
            branch=branch,
            micro_branch=exercise_type,
            title=format_template.get("title", f"Ejercicio de {branch}").format(
                **content_data
            ),
            description=format_template.get(
                "description", f"Ejercicio de práctica en {branch}"
            ).format(**content_data),
            difficulty=difficulty,
            content=format_template.get(
                "content_template", "Ejercicio de práctica"
            ).format(**content_data),
            solution=format_template.get(
                "solution_template", "Solución del ejercicio"
            ).format(**content_data),
            hints=content_data.get("hints", []),
            tags=content_data.get("tags", [branch, exercise_type, difficulty]),
            created_date=date,
            estimated_time=self._estimate_time(difficulty, exercise_type),
            points=self._calculate_points(difficulty, exercise_type),
            questions=content_data.get("questions", []),
        )

        return exercise

    async def _generate_content_data(
        self, branch: str, exercise_type: str, difficulty: str
    ) -> Dict[str, Any]:
        """Generar datos específicos para el contenido del ejercicio"""

        # Datos específicos por rama y tipo de ejercicio
        content_data = {
            "hints": [
                "Lee cuidadosamente el problema",
                "Divide el problema en pasos más pequeños",
            ],
            "tags": [branch, exercise_type, difficulty],
        }

        # 1. LENGUA Y LINGÜÍSTICA
        if branch == "lengua_y_lingüística":
            if exercise_type == "gramática":
                oraciones = {
                    "básico": ["El niño juega en el parque", "La casa es grande"],
                    "intermedio": [
                        "Los estudiantes estudian matemáticas",
                        "El profesor explica la lección",
                    ],
                    "avanzado": [
                        "El investigador que descubrió la vacuna recibió el premio",
                        "La empresa que fabrica coches eléctricos es innovadora",
                    ],
                }
                content_data.update(
                    {
                        "tipo_análisis": "oración simple",
                        "oración": random.choice(oraciones[difficulty]),
                        "análisis_detallado": "Análisis morfosintáctico completo",
                        "categorías": "Sustantivo, verbo, adjetivo, determinante",
                    }
                )

        # 2. MATEMÁTICAS
        elif branch == "matemáticas":
            if exercise_type == "álgebra":
                equations = {
                    "básico": ["2x + 3 = 7", "x² - 4 = 0"],
                    "intermedio": ["x² + 5x + 6 = 0", "2x³ - 8x = 0"],
                    "avanzado": ["x⁴ - 16 = 0", "log₂(x) = 3"],
                }
                content_data.update(
                    {
                        "ecuación": random.choice(equations[difficulty]),
                        "pasos_solución": "1. Aislar la variable\n2. Aplicar operaciones inversas",
                        "respuesta": "x = 2",
                    }
                )
            elif exercise_type == "cálculo":
                funciones = {
                    "básico": ["x²", "2x + 1"],
                    "intermedio": ["sin(x)", "e^x"],
                    "avanzado": ["ln(x² + 1)", "∫x²dx"],
                }
                content_data.update(
                    {
                        "operación": "derivada",
                        "función": random.choice(funciones[difficulty]),
                        "pasos_cálculo": "Aplicar reglas de derivación",
                        "resultado": "2x",
                    }
                )

        # 3. COMPUTACIÓN Y PROGRAMACIÓN
        elif branch == "computación_y_programación":
            if exercise_type == "algoritmos":
                algorithms = {
                    "básico": ["búsqueda lineal", "ordenamiento burbuja", "factorial"],
                    "intermedio": ["quicksort", "búsqueda binaria", "fibonacci"],
                    "avanzado": [
                        "algoritmo de Dijkstra",
                        "programación dinámica",
                        "backtracking",
                    ],
                }
                content_data.update(
                    {
                        "algoritmo": random.choice(algorithms[difficulty]),
                        "problema": "ordenar una lista de números",
                        "lenguaje": random.choice(["Python", "JavaScript", "Java"]),
                        "descripción_problema": "ordene una lista de números enteros",
                        "solución": "def ordenar_lista(lista):\n    return sorted(lista)",
                    }
                )

        # 4. CIENCIA DE DATOS E IA
        elif branch == "ciencia_de_datos_e_ia":
            if exercise_type == "modelado":
                modelos = {
                    "básico": ["regresión lineal", "clasificación binaria"],
                    "intermedio": ["random forest", "SVM"],
                    "avanzado": ["redes neuronales", "deep learning"],
                }
                content_data.update(
                    {
                        "tipo_modelo": random.choice(modelos[difficulty]),
                        "variable_objetivo": "predecir ventas",
                        "features": "edad, ingresos, ubicación",
                        "código_modelo": "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()",
                    }
                )

        # 5. FÍSICA
        elif branch == "física":
            if exercise_type == "mecánica":
                content_data.update(
                    {
                        "tipo_problema": "movimiento rectilíneo uniforme",
                        "masa": random.randint(1, 10),
                        "velocidad": random.randint(5, 20),
                        "descripción_problema": "Calcula la distancia recorrida en 10 segundos",
                        "principio": "d = v × t",
                        "pasos_solución": f"d = velocidad × tiempo\nd = {random.randint(5, 20)} × 10 = {random.randint(5, 20) * 10} m",
                        "resultado": f"{random.randint(5, 20) * 10} metros",
                    }
                )

        # 6. QUÍMICA
        elif branch == "química":
            if exercise_type == "química_orgánica":
                compuestos = {
                    "básico": ["etanol", "metano"],
                    "intermedio": ["benceno", "ácido acético"],
                    "avanzado": ["proteínas", "ADN"],
                }
                content_data.update(
                    {
                        "compuesto_orgánico": random.choice(compuestos[difficulty]),
                        "compuesto": random.choice(compuestos[difficulty]),
                        "reactivos_iniciales": "compuestos básicos",
                        "pasos_síntesis": "1. Preparación de reactivos\n2. Reacción principal\n3. Purificación",
                        "mecanismo": "Reacción de sustitución nucleofílica",
                    }
                )

        # 7. BIOLOGÍA
        elif branch == "biología":
            if exercise_type == "genética":
                content_data.update(
                    {
                        "tipo_genética": "herencia mendeliana",
                        "descripción_población": "una población con genes dominantes y recesivos",
                        "pregunta_problema": "¿Cuál es la probabilidad de que un individuo sea heterocigoto?",
                        "principio_genético": "Leyes de Mendel",
                        "pasos_solución": "1. Identificar genotipos\n2. Aplicar cuadro de Punnett\n3. Calcular probabilidades",
                        "respuesta": "25% de probabilidad",
                    }
                )

        # 8. MEDICINA Y SALUD
        elif branch == "medicina_y_salud":
            if exercise_type == "diagnóstico":
                content_data.update(
                    {
                        "condición_médica": "diabetes tipo 2",
                        "síntomas": "sed excesiva, fatiga, visión borrosa",
                        "historia_clínica": "Paciente de 45 años con antecedentes familiares",
                        "diagnósticos": "Diabetes tipo 2, prediabetes, diabetes tipo 1",
                        "pruebas": "Glucosa en ayunas, hemoglobina glicosilada",
                        "tratamiento": "Dieta, ejercicio, medicación oral",
                    }
                )

        # 9. NEUROCIENCIA Y PSICOLOGÍA
        elif branch == "neurociencia_y_psicología":
            if exercise_type == "psicología_cognitiva":
                content_data.update(
                    {
                        "proceso_cognitivo": "memoria de trabajo",
                        "contexto": "aprendizaje de idiomas",
                        "mecanismos": "Codificación, almacenamiento, recuperación",
                        "implicaciones": "Mejora del rendimiento académico",
                    }
                )

        # 10. INGENIERÍA
        elif branch == "ingeniería":
            if exercise_type == "ingeniería_eléctrica":
                content_data.update(
                    {
                        "tipo_circuito": "amplificador operacional",
                        "especificaciones": "ganancia de 10, alimentación ±15V",
                        "esquema": "Diagrama del circuito con op-amp",
                        "cálculos": "Ganancia = Rf/Ri = 10",
                        "componentes": "Op-amp, resistencias, fuente de alimentación",
                    }
                )

        # 11. ELECTRÓNICA Y IOT
        elif branch == "electrónica_y_iot":
            if exercise_type == "microcontroladores":
                content_data.update(
                    {
                        "microcontrolador": "Arduino Uno",
                        "tarea_específica": "controlar un LED con sensor de luz",
                        "código_programa": "void setup() {\n  pinMode(LED_PIN, OUTPUT);\n}\nvoid loop() {\n  // Control del LED\n}",
                        "configuración": "Pin 13 como salida, sensor en pin A0",
                    }
                )

        # 12. CIBERSEGURIDAD Y CRIPTOGRAFÍA
        elif branch == "ciberseguridad_y_criptografía":
            if exercise_type == "criptografía":
                content_data.update(
                    {
                        "algoritmo_criptográfico": "AES-256",
                        "aplicación": "cifrado de archivos",
                        "implementación": "from cryptography.fernet import Fernet\nkey = Fernet.generate_key()",
                        "análisis_seguridad": "Resistente a ataques de fuerza bruta",
                    }
                )

        # 13. SISTEMAS/DEVOPS/REDES
        elif branch == "sistemas_devops_redes":
            if exercise_type == "devops":
                content_data.update(
                    {
                        "proyecto": "aplicación web",
                        "tecnologías": "Docker, Kubernetes, Jenkins",
                        "pipeline_yaml": "stages:\n  - build\n  - test\n  - deploy",
                        "etapas": "Build, Test, Deploy",
                        "herramientas": "Git, Docker, Jenkins, Kubernetes",
                    }
                )
            elif exercise_type == "redes":
                content_data.update(
                    {
                        "tipo_red": "LAN",
                        "organización": "empresa mediana",
                        "requisitos": "100 usuarios, alta disponibilidad",
                        "topología": "Topología en estrella con switch central",
                        "configuración_ip": "192.168.1.0/24",
                        "seguridad": "Firewall, VLANs, acceso controlado",
                    }
                )

        # 14. CIENCIAS DE LA TIERRA Y CLIMA
        elif branch == "ciencias_de_la_tierra_y_clima":
            if exercise_type == "meteorología":
                content_data.update(
                    {
                        "fenómeno": "huracán",
                        "región": "Caribe",
                        "causas": "Temperatura del mar, humedad, vientos",
                        "patrones": "Formación, intensificación, disipación",
                        "predicciones": "Modelos numéricos de predicción",
                    }
                )

        # 15. ASTRONOMÍA Y ESPACIO
        elif branch == "astronomía_y_espacio":
            if exercise_type == "astrofísica":
                content_data.update(
                    {
                        "objeto_astronómico": "estrella de neutrones",
                        "parámetros": "masa, radio, densidad",
                        "propiedades": "Masa solar, radio de 10km, densidad nuclear",
                        "evolución": "Colapso de supernova",
                        "implicaciones": "Estudio de materia exótica",
                    }
                )

        # 16. ECONOMÍA Y FINANZAS
        elif branch == "economía_y_finanzas":
            if exercise_type == "microeconomía":
                content_data.update(
                    {
                        "mercado": "mercado de smartphones",
                        "factores_económicos": "oferta, demanda, elasticidad",
                        "oferta_demanda": "Curvas de oferta y demanda",
                        "equilibrio": "Precio y cantidad de equilibrio",
                        "políticas": "Impuestos, subsidios, regulaciones",
                    }
                )

        # 17. EMPRESA Y EMPRENDIMIENTO
        elif branch == "empresa_y_emprendimiento":
            if exercise_type == "estrategia":
                content_data.update(
                    {
                        "empresa": "startup tecnológica",
                        "sector": "inteligencia artificial",
                        "análisis_swot": "Fortalezas, debilidades, oportunidades, amenazas",
                        "objetivos": "Crecimiento de mercado, innovación",
                        "acciones": "Desarrollo de producto, marketing digital",
                    }
                )

        # 18. DERECHO Y POLÍTICAS PÚBLICAS
        elif branch == "derecho_y_políticas_públicas":
            if exercise_type == "derecho_civil":
                content_data.update(
                    {
                        "área_derecho_civil": "contratos",
                        "tipo_caso": "incumplimiento contractual",
                        "normativa": "Código Civil",
                        "hechos": "Parte incumple obligación contractual",
                        "resolución": "Resolución del contrato, indemnización",
                    }
                )

        # 19. SOCIOLOGÍA Y ANTROPOLOGÍA
        elif branch == "sociología_y_antropología":
            if exercise_type == "sociología_urbana":
                content_data.update(
                    {
                        "fenómeno_urbano": "gentrificación",
                        "ciudad": "Barcelona",
                        "factores_sociales": "Migración, cambio económico, políticas urbanas",
                        "impacto": "Cambio demográfico, aumento de precios",
                        "tendencias": "Polarización social, transformación urbana",
                    }
                )

        # 20. EDUCACIÓN Y PEDAGOGÍA
        elif branch == "educación_y_pedagogía":
            if exercise_type == "diseño_curricular":
                content_data.update(
                    {
                        "materia": "matemáticas",
                        "nivel_educativo": "secundaria",
                        "objetivos": "Desarrollo del pensamiento lógico",
                        "contenidos": "Álgebra, geometría, estadística",
                        "evaluación": "Proyectos, exámenes, participación",
                    }
                )

        # 21. HISTORIA
        elif branch == "historia":
            if exercise_type == "historia_contemporánea":
                content_data.update(
                    {
                        "evento": "Revolución Industrial",
                        "contexto": "Europa del siglo XIX",
                        "antecedentes": "Cambios tecnológicos, sociales",
                        "desarrollo": "Mecanización, urbanización",
                        "consecuencias": "Cambio social, económico, político",
                    }
                )

        # 22. GEOGRAFÍA Y GEO-POLÍTICA
        elif branch == "geografía_y_geo_política":
            if exercise_type == "geopolítica":
                content_data.update(
                    {
                        "región": "Medio Oriente",
                        "factores": "Recursos energéticos, conflictos religiosos",
                        "conflictos": "Tensiones regionales, intereses internacionales",
                        "intereses": "Petróleo, seguridad, influencia política",
                        "tendencias": "Cambio de alianzas, nuevas potencias",
                    }
                )

        # 23. ARTE, MÚSICA Y CULTURA
        elif branch == "arte_música_y_cultura":
            if exercise_type == "composición_musical":
                content_data.update(
                    {
                        "estilo": "clásico",
                        "instrumentos": "piano y violín",
                        "notación_musical": "Partitura en Do mayor",
                        "estructura": "Forma sonata: exposición, desarrollo, recapitulación",
                        "análisis": "Armonía, melodía, ritmo",
                    }
                )
            elif exercise_type == "análisis_artístico":
                content_data.update(
                    {
                        "obra_arte": "La Gioconda",
                        "perspectiva": "histórica",
                        "elementos_formales": "Composición, color, técnica",
                        "significado": "Retrato renacentista",
                        "contexto": "Florencia del siglo XVI",
                    }
                )

        # 24. LITERATURA Y ESCRITURA
        elif branch == "literatura_y_escritura":
            if exercise_type == "análisis_literario":
                content_data.update(
                    {
                        "obra_literaria": "Don Quijote",
                        "perspectiva": "psicológica",
                        "tema": "Locura y realidad",
                        "estructura": "Novela picaresca, estructura episódica",
                        "recursos_literarios": "Ironía, parodia, simbolismo",
                    }
                )

        # 25. MEDIOS Y COMUNICACIÓN
        elif branch == "medios_y_comunicación":
            if exercise_type == "periodismo":
                content_data.update(
                    {
                        "tema": "cambio climático",
                        "medio_comunicación": "periódico digital",
                        "estructura": "Titular, lead, desarrollo, conclusión",
                        "contenido": "Datos científicos, testimonios, análisis",
                        "fuentes": "Científicos, organizaciones, documentos oficiales",
                    }
                )
            elif exercise_type == "comunicación_digital":
                content_data.update(
                    {
                        "organización": "startup tecnológica",
                        "canales": "Redes sociales, email marketing, blog",
                        "contenido": "Contenido educativo, casos de éxito",
                        "métricas": "Engagement, conversiones, ROI",
                    }
                )

        # 26. DISEÑO Y UX
        elif branch == "diseño_y_ux":
            if exercise_type == "ux_ui":
                content_data.update(
                    {
                        "aplicación": "app de delivery",
                        "usuarios": "personas de 25-45 años",
                        "user_personas": "Perfiles de usuarios objetivo",
                        "wireframes": "Bocetos de pantallas principales",
                        "prototipo": "Prototipo interactivo en Figma",
                    }
                )

        # 27. DEPORTES Y ESPORTS
        elif branch == "deportes_y_esports":
            if exercise_type == "análisis_deportivo":
                content_data.update(
                    {
                        "deporte": "fútbol",
                        "factores": "técnica, táctica, condición física",
                        "técnica": "Control, pase, disparo",
                        "estrategia": "Formación 4-3-3, presión alta",
                        "mejoras": "Entrenamiento específico, análisis de video",
                    }
                )

        # 28. JUEGOS Y ENTRETENIMIENTO
        elif branch == "juegos_y_entretenimiento":
            if exercise_type == "diseño_juegos":
                content_data.update(
                    {
                        "tipo_juego": "estrategia",
                        "plataforma": "PC",
                        "concepto": "Juego de gestión de recursos",
                        "mecánicas": "Recolección, construcción, combate",
                        "narrativa": "Historia épica de supervivencia",
                    }
                )

        # 29. HOGAR, DIY Y REPARACIONES
        elif branch == "hogar_diy_y_reparaciones":
            if exercise_type == "bricolaje":
                content_data.update(
                    {
                        "tipo_proyecto": "estantería",
                        "espacio": "sala de estar",
                        "materiales": "Madera, tornillos, barniz",
                        "herramientas": "Taladro, sierra, destornillador",
                        "pasos": "Medir, cortar, ensamblar, barnizar",
                    }
                )

        # 30. COCINA Y NUTRICIÓN
        elif branch == "cocina_y_nutrición":
            if exercise_type == "gastronomía":
                content_data.update(
                    {
                        "plato": "paella valenciana",
                        "ingredientes": "Arroz, pollo, conejo, verduras",
                        "preparación": "Sofreír, añadir caldo, cocer a fuego lento",
                        "técnicas": "Sofrito, cocción en paellera",
                    }
                )

        # 31. VIAJES E IDIOMAS
        elif branch == "viajes_e_idiomas":
            if exercise_type == "planificación_viajes":
                content_data.update(
                    {
                        "días": "7",
                        "destino": "Japón",
                        "ruta": "Tokio, Kioto, Osaka",
                        "actividades": "Templos, gastronomía, tecnología",
                        "presupuesto": "2000€ por persona",
                    }
                )

        # 32. VIDA DIARIA, LEGAL PRÁCTICO Y TRÁMITES
        elif branch == "vida_diaria_legal_práctico_y_trámites":
            if exercise_type == "trámites_burocráticos":
                content_data.update(
                    {
                        "tipo_trámite": "DNI",
                        "documentos": "Certificado de nacimiento, fotos",
                        "pasos": "Solicitud online, cita previa, entrega",
                        "plazos": "15 días hábiles",
                    }
                )

        return content_data

    def _get_active_branches(self) -> List[str]:
        """Obtener lista de ramas activas"""
        branches = []
        if self.branches_path.exists():
            for branch_dir in self.branches_path.iterdir():
                if branch_dir.is_dir():
                    branch_name = branch_dir.name
                    # Verificar si es una rama válida
                    if branch_name in self.exercise_templates:
                        branches.append(branch_name)

        return branches

    def _exercise_already_generated(self, branch: str, date: datetime) -> bool:
        """Verificar si ya se generó un ejercicio para esta rama en esta fecha"""
        date_str = date.strftime("%Y-%m-%d")
        exercise_file = self.exercises_dir / f"{branch}_{date_str}.json"
        return exercise_file.exists()

    def _generate_exercise_id(self, branch: str, date: datetime) -> str:
        """Generar ID único para el ejercicio"""
        date_str = date.strftime("%Y%m%d")
        return f"{branch}_{date_str}_{hashlib.md5(f'{branch}{date_str}'.encode()).hexdigest()[:8]}"

    def _estimate_time(self, difficulty: str, exercise_type: str) -> int:
        """Estimar tiempo de resolución en minutos"""
        base_times = {"básico": 10, "intermedio": 20, "avanzado": 35}
        return base_times.get(difficulty, 15)

    def _calculate_points(self, difficulty: str, exercise_type: str) -> int:
        """Calcular puntos del ejercicio"""
        base_points = {"básico": 10, "intermedio": 20, "avanzado": 35}
        return base_points.get(difficulty, 15)

    def _save_exercise(self, exercise: Exercise):
        """Guardar ejercicio en archivo JSON"""
        date_str = exercise.created_date.strftime("%Y-%m-%d")
        exercise_file = self.exercises_dir / f"{exercise.branch}_{date_str}.json"

        # Convertir datetime a string para JSON
        exercise_dict = asdict(exercise)
        exercise_dict["created_date"] = exercise.created_date.isoformat()

        with open(exercise_file, "w", encoding="utf-8") as f:
            json.dump(exercise_dict, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Ejercicio guardado: {exercise_file}")

    def get_today_exercises(self) -> Dict[str, Exercise]:
        """Obtener ejercicios de hoy"""
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        exercises = {}

        for branch in self._get_active_branches():
            exercise_file = self.exercises_dir / f"{branch}_{date_str}.json"
            if exercise_file.exists():
                try:
                    with open(exercise_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["created_date"] = datetime.fromisoformat(
                            data["created_date"]
                        )
                        exercises[branch] = Exercise(**data)
                except Exception as e:
                    self.logger.error(f"Error cargando ejercicio de {branch}: {e}")

        return exercises

    def start_scheduler(self):
        """Iniciar el scheduler para generación automática"""
        # Programar generación diaria a las 12:00 PM (mediodía)
        self.scheduler.add_job(
            self.generate_daily_exercises,
            CronTrigger(hour=12, minute=0),
            id="daily_exercise_generation",
            name="Generación diaria de ejercicios",
        )

        self.scheduler.start()
        self.logger.info("Scheduler de ejercicios diarios iniciado")

    def stop_scheduler(self):
        """Detener el scheduler"""
        self.scheduler.shutdown()
        self.logger.info("Scheduler de ejercicios diarios detenido")

    async def generate_exercises_for_branch(
        self, branch: str, date: Optional[datetime] = None
    ) -> Optional[Exercise]:
        """Generar ejercicio específico para una rama en una fecha dada"""
        if date is None:
            date = datetime.now()

        day_of_week = date.weekday()
        difficulty = self.difficulty_schedule[day_of_week]

        return await self._generate_branch_exercise(branch, difficulty, date)


# Función de utilidad para usar el generador
async def main():
    """Función principal para probar el generador"""
    generator = DailyExerciseGenerator()

    # Generar ejercicios para hoy
    exercises = await generator.generate_daily_exercises()

    print(f"Ejercicios generados: {len(exercises)}")
    for branch, exercise in exercises.items():
        print(f"\n{branch}:")
        print(f"  Título: {exercise.title}")
        print(f"  Dificultad: {exercise.difficulty}")
        print(f"  Puntos: {exercise.points}")


if __name__ == "__main__":
    asyncio.run(main())
