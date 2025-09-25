#!/usr/bin/env python3
"""
Script para expandir el dataset HEAD-QA con muchas más preguntas de opción múltiple
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def create_expanded_headqa_dataset():
    """Crear dataset HEAD-QA expandido con muchas más preguntas"""

    # Dataset expandido con preguntas de opción múltiple por ramas
    expanded_headqa = {
        "train": [
            # MÉDICO
            {
                "question": "¿Cuál es el síntoma más común de la hipertensión arterial?",
                "choices": [
                    "Dolor de cabeza intenso",
                    "Dolor en el pecho",
                    "Puede ser asintomática",
                    "Fiebre alta",
                ],
                "answer": 2,
                "explanation": "La hipertensión arterial a menudo es asintomática, por lo que se le llama 'el asesino silencioso'.",
                "domain": "medical",
            },
            {
                "question": "¿Qué es la diabetes mellitus tipo 2?",
                "choices": [
                    "Una enfermedad autoinmune",
                    "Una resistencia a la insulina",
                    "Una infección viral",
                    "Una enfermedad genética rara",
                ],
                "answer": 1,
                "explanation": "La diabetes tipo 2 se caracteriza por resistencia a la insulina y deficiencia relativa de insulina.",
                "domain": "medicalff",
            },
            {
                "question": "¿Cuál es la función principal del corazón?",
                "choices": [
                    "Producir hormonas",
                    "Bombear sangre",
                    "Filtrar toxinas",
                    "Producir enzimas",
                ],
                "answer": 1,
                "explanation": "El corazón es el órgano principal del sistema circulatorio que bombea sangre a todo el cuerpo.",
                "domain": "medical",
            },
            {
                "question": "¿Qué son los antibióticos?",
                "choices": [
                    "Medicamentos que combaten bacterias",
                    "Vitaminas",
                    "Hormonas",
                    "Enzimas digestivas",
                ],
                "answer": 0,
                "explanation": "Los antibióticos son medicamentos que combaten infecciones bacterianas.",
                "domain": "medicalff",
            },
            {
                "question": "¿Cuál es el componente principal de la sangre?",
                "choices": [
                    "Glóbulos rojos",
                    "Plasma",
                    "Plaquetas",
                    "Glóbulos blancos",
                ],
                "answer": 1,
                "explanation": "El plasma es el componente líquido principal de la sangre, constituyendo aproximadamente el 55%.",
                "domain": "medical",
            },
            # TÉCNICO
            {
                "question": "¿Qué es el machine learning?",
                "choices": [
                    "Un tipo de hardware",
                    "Algoritmos que aprenden de datos",
                    "Un lenguaje de programación",
                    "Un sistema operativo",
                ],
                "answer": 1,
                "explanation": "El machine learning es una rama de la IA que permite a las computadoras aprender sin ser programadas explícitamente.",
                "domain": "technicalff",
            },
            {
                "question": "¿Qué es una red neuronal?",
                "choices": [
                    "Un tipo de cable de red",
                    "Un modelo computacional inspirado en el cerebro",
                    "Un protocolo de internet",
                    "Un dispositivo de almacenamiento",
                ],
                "answer": 1,
                "explanation": "Una red neuronal es un modelo computacional inspirado en las conexiones neuronales del cerebro humano.",
                "domain": "technical",
            },
            {
                "question": "¿Qué es la inteligencia artificial?",
                "choices": [
                    "Solo robots humanoides",
                    "Sistemas que simulan inteligencia humana",
                    "Un tipo de computadora",
                    "Un algoritmo específico",
                ],
                "answer": 1,
                "explanation": "La IA se refiere a sistemas que pueden realizar tareas que normalmente requieren inteligencia humana.",
                "domain": "technicalff",
            },
            {
                "question": "¿Qué es el deep learning?",
                "choices": [
                    "Aprendizaje superficial",
                    "Redes neuronales con múltiples capas",
                    "Un tipo de base de datos",
                    "Un protocolo de comunicación",
                ],
                "answer": 1,
                "explanation": "El deep learning usa redes neuronales con múltiples capas para aprender patrones complejos.",
                "domain": "technical",
            },
            {
                "question": "¿Qué es la computación en la nube?",
                "choices": [
                    "Servicios de internet",
                    "Almacenamiento y procesamiento remoto",
                    "Un tipo de software",
                    "Un protocolo de red",
                ],
                "answer": 1,
                "explanation": "La computación en la nube proporciona servicios de almacenamiento y procesamiento a través de internet.",
                "domain": "technicalff",
            },
            # PROGRAMACIÓN
            {
                "question": "¿Qué lenguaje de programación es más adecuado para análisis de datos?",
                "choices": ["Java", "Python", "C++", "JavaScript"],
                "answer": 1,
                "explanation": "Python es el lenguaje más popular para análisis de datos debido a sus librerías como pandas, numpy y scikit-learn.",
                "domain": "programming",
            },
            {
                "question": "¿Qué es Git?",
                "choices": [
                    "Un lenguaje de programación",
                    "Un sistema de control de versiones",
                    "Un editor de código",
                    "Un compilador",
                ],
                "answer": 1,
                "explanation": "Git es un sistema de control de versiones que permite rastrear cambios en el código fuente.",
                "domain": "programmingff",
            },
            {
                "question": "¿Qué es una API?",
                "choices": [
                    "Un tipo de base de datos",
                    "Una interfaz de programación de aplicaciones",
                    "Un lenguaje de programación",
                    "Un sistema operativo",
                ],
                "answer": 1,
                "explanation": "Una API es una interfaz que permite que diferentes aplicaciones se comuniquen entre sí.",
                "domain": "programming",
            },
            {
                "question": "¿Qué es el debugging?",
                "choices": [
                    "Crear código",
                    "Encontrar y corregir errores",
                    "Optimizar rendimiento",
                    "Documentar código",
                ],
                "answer": 1,
                "explanation": "El debugging es el proceso de encontrar y corregir errores en el código de programación.",
                "domain": "programmingff",
            },
            {
                "question": "¿Qué es un algoritmo?",
                "choices": [
                    "Un tipo de hardware",
                    "Una secuencia de pasos para resolver un problema",
                    "Un lenguaje de programación",
                    "Un sistema operativo",
                ],
                "answer": 1,
                "explanation": "Un algoritmo es una secuencia finita de instrucciones para resolver un problema específico.",
                "domain": "programming",
            },
            # LEGAL
            {
                "question": "¿Qué es el derecho constitucional?",
                "choices": [
                    "Derecho penal",
                    "Derecho que estudia la Constitución",
                    "Derecho civil",
                    "Derecho laboral",
                ],
                "answer": 1,
                "explanation": "El derecho constitucional estudia la organización del Estado y los derechos fundamentales.",
                "domain": "legalff",
            },
            {
                "question": "¿Qué son los derechos fundamentales?",
                "choices": [
                    "Solo derechos civiles",
                    "Derechos humanos reconocidos por la Constitución",
                    "Derechos económicos",
                    "Derechos políticos",
                ],
                "answer": 1,
                "explanation": "Los derechos fundamentales son aquellos derechos humanos reconocidos y protegidos por la Constitución.",
                "domain": "legal",
            },
            {
                "question": "¿Qué es el habeas corpus?",
                "choices": [
                    "Un tipo de contrato",
                    "Un recurso para proteger la libertad personal",
                    "Un procedimiento penal",
                    "Un derecho de propiedad",
                ],
                "answer": 1,
                "explanation": "El habeas corpus es un recurso legal para proteger la libertad personal contra detenciones arbitrarias.",
                "domain": "legalff",
            },
            {
                "question": "¿Qué es la presunción de inocencia?",
                "choices": [
                    "Un principio legal fundamental",
                    "Un tipo de sentencia",
                    "Un procedimiento judicial",
                    "Un derecho de propiedad",
                ],
                "answer": 0,
                "explanation": "La presunción de inocencia establece que toda persona es inocente hasta que se demuestre lo contrario.",
                "domain": "legal",
            },
            {
                "question": "¿Qué es el debido proceso?",
                "choices": [
                    "Un tipo de contrato",
                    "Un procedimiento legal justo",
                    "Un derecho de propiedad",
                    "Un tipo de sentencia",
                ],
                "answer": 1,
                "explanation": "El debido proceso garantiza que los procedimientos legales sean justos y transparentes.",
                "domain": "legalff",
            },
            # EMPRESARIAL
            {
                "question": "¿Qué es el marketing digital?",
                "choices": [
                    "Solo redes sociales",
                    "Estrategias comerciales en internet",
                    "Un tipo de publicidad",
                    "Un sistema de ventas",
                ],
                "answer": 1,
                "explanation": "El marketing digital incluye todas las estrategias publicitarias y comerciales en medios digitales.",
                "domain": "business",
            },
            {
                "question": "¿Qué es el ROI?",
                "choices": [
                    "Un tipo de impuesto",
                    "Retorno sobre la inversión",
                    "Un indicador de ventas",
                    "Un tipo de contrato",
                ],
                "answer": 1,
                "explanation": "El ROI (Return on Investment) mide la rentabilidad de una inversión en relación al costo.",
                "domain": "businessff",
            },
            {
                "question": "¿Qué es la economía de escala?",
                "choices": [
                    "Un tipo de impuesto",
                    "Reducción de costos al aumentar producción",
                    "Un indicador financiero",
                    "Un tipo de mercado",
                ],
                "answer": 1,
                "explanation": "Las economías de escala ocurren cuando los costos unitarios disminuyen al aumentar la producción.",
                "domain": "business",
            },
            {
                "question": "¿Qué es la oferta y demanda?",
                "choices": [
                    "Un tipo de contrato",
                    "El principio básico de la economía de mercado",
                    "Un indicador financiero",
                    "Un tipo de impuesto",
                ],
                "answer": 1,
                "explanation": "La oferta y demanda es el principio fundamental que determina los precios en una economía de mercado.",
                "domain": "businessff",
            },
            {
                "question": "¿Qué es la competencia perfecta?",
                "choices": [
                    "Un tipo de monopolio",
                    "Un mercado con muchos compradores y vendedores",
                    "Un tipo de oligopolio",
                    "Un mercado regulado",
                ],
                "answer": 1,
                "explanation": "La competencia perfecta es un modelo de mercado con muchos compradores y vendedores de productos idénticos.",
                "domain": "business",
            },
            # CIENTÍFICO
            {
                "question": "¿Qué es el método científico?",
                "choices": [
                    "Un tipo de experimento",
                    "Un proceso sistemático de investigación",
                    "Una teoría",
                    "Una hipótesis",
                ],
                "answer": 1,
                "explanation": "El método científico es un proceso sistemático para investigar fenómenos y adquirir conocimiento.",
                "domain": "scientificff",
            },
            {
                "question": "¿Qué es una hipótesis?",
                "choices": [
                    "Una teoría probada",
                    "Una explicación tentativa",
                    "Una ley científica",
                    "Un experimento",
                ],
                "answer": 1,
                "explanation": "Una hipótesis es una explicación tentativa que puede ser probada mediante experimentación.",
                "domain": "scientific",
            },
            {
                "question": "¿Qué es la teoría de la evolución?",
                "choices": [
                    "Una teoría sobre el origen del universo",
                    "Una teoría sobre el cambio de las especies",
                    "Una teoría sobre la gravedad",
                    "Una teoría sobre la electricidad",
                ],
                "answer": 1,
                "explanation": "La teoría de la evolución explica cómo las especies cambian a lo largo del tiempo mediante selección natural.",
                "domain": "scientificff",
            },
            {
                "question": "¿Qué es la fotosíntesis?",
                "choices": [
                    "Un proceso de respiración",
                    "Un proceso de conversión de energía solar",
                    "Un proceso de digestión",
                    "Un proceso de reproducción",
                ],
                "answer": 1,
                "explanation": "La fotosíntesis es el proceso mediante el cual las plantas convierten la energía solar en energía química.",
                "domain": "scientific",
            },
            {
                "question": "¿Qué es la gravedad?",
                "choices": [
                    "Una fuerza de repulsión",
                    "Una fuerza de atracción entre masas",
                    "Un tipo de energía",
                    "Un tipo de materia",
                ],
                "answer": 1,
                "explanation": "La gravedad es una fuerza fundamental de atracción que existe entre todos los objetos con masa.",
                "domain": "scientificff",
            },
            # MATEMÁTICAS
            {
                "question": "¿Cuál es la fórmula del área de un círculo?",
                "choices": ["A = l × w", "A = πr²", "A = ½bh", "A = s²"],
                "answer": 1,
                "explanation": "El área de un círculo se calcula multiplicando π por el radio al cuadrado.",
                "domain": "mathematics",
            },
            {
                "question": "¿Qué es el teorema de Pitágoras?",
                "choices": ["a² + b² = c²", "a + b = c", "a × b = c", "a ÷ b = c"],
                "answer": 0,
                "explanation": "El teorema de Pitágoras establece que en un triángulo rectángulo, a² + b² = c².",
                "domain": "mathematicsff",
            },
            {
                "question": "¿Qué es una ecuación cuadrática?",
                "choices": [
                    "Una ecuación de primer grado",
                    "Una ecuación de segundo grado",
                    "Una ecuación de tercer grado",
                    "Una ecuación lineal",
                ],
                "answer": 1,
                "explanation": "Una ecuación cuadrática es una ecuación polinómica de segundo grado.",
                "domain": "mathematics",
            },
            {
                "question": "¿Qué es la derivada?",
                "choices": [
                    "Una integral",
                    "La tasa de cambio instantánea",
                    "Una función",
                    "Una constante",
                ],
                "answer": 1,
                "explanation": "La derivada mide la tasa de cambio instantánea de una función en un punto específico.",
                "domain": "mathematicsff",
            },
            {
                "question": "¿Qué es la probabilidad?",
                "choices": [
                    "Una certeza",
                    "Una medida de incertidumbre",
                    "Una estadística",
                    "Una media",
                ],
                "answer": 1,
                "explanation": "La probabilidad es una medida de la incertidumbre asociada a un evento.",
                "domain": "mathematics",
            },
            # FÍSICA
            {
                "question": "¿Qué es la ley de gravitación universal?",
                "choices": [
                    "Una ley sobre electricidad",
                    "Una ley sobre la atracción entre masas",
                    "Una ley sobre magnetismo",
                    "Una ley sobre energía",
                ],
                "answer": 1,
                "explanation": "La ley de gravitación universal establece que dos cuerpos se atraen con una fuerza proporcional a sus masas.",
                "domain": "physicsff",
            },
            {
                "question": "¿Qué es la energía cinética?",
                "choices": [
                    "Energía de posición",
                    "Energía de movimiento",
                    "Energía térmica",
                    "Energía potencial",
                ],
                "answer": 1,
                "explanation": "La energía cinética es la energía que posee un objeto debido a su movimiento.",
                "domain": "physics",
            },
            {
                "question": "¿Qué es la velocidad?",
                "choices": [
                    "Una fuerza",
                    "La rapidez con dirección",
                    "Una aceleración",
                    "Una masa",
                ],
                "answer": 1,
                "explanation": "La velocidad es la rapidez con la que un objeto se mueve en una dirección específica.",
                "domain": "physicsff",
            },
            {
                "question": "¿Qué es la masa?",
                "choices": [
                    "Un peso",
                    "La cantidad de materia",
                    "Una fuerza",
                    "Una energía",
                ],
                "answer": 1,
                "explanation": "La masa es la cantidad de materia que contiene un objeto.",
                "domain": "physics",
            },
            {
                "question": "¿Qué es la temperatura?",
                "choices": [
                    "Una medida de calor",
                    "Una medida de energía térmica",
                    "Una medida de presión",
                    "Una medida de volumen",
                ],
                "answer": 1,
                "explanation": "La temperatura es una medida de la energía térmica promedio de las partículas de un sistema.",
                "domain": "physicsff",
            },
            # QUÍMICA
            {
                "question": "¿Qué es una reacción química?",
                "choices": [
                    "Un cambio físico",
                    "Un cambio en la composición de sustancias",
                    "Un cambio de estado",
                    "Un cambio de temperatura",
                ],
                "answer": 1,
                "explanation": "Una reacción química es un proceso donde las sustancias se transforman en nuevas sustancias.",
                "domain": "chemistry",
            },
            {
                "question": "¿Qué es la tabla periódica?",
                "choices": [
                    "Una lista de elementos",
                    "Una organización sistemática de elementos",
                    "Una tabla de compuestos",
                    "Una tabla de reacciones",
                ],
                "answer": 1,
                "explanation": "La tabla periódica es una organización sistemática de los elementos químicos.",
                "domain": "chemistryff",
            },
            {
                "question": "¿Qué es un átomo?",
                "choices": [
                    "Una molécula",
                    "La unidad básica de la materia",
                    "Un compuesto",
                    "Una reacción",
                ],
                "answer": 1,
                "explanation": "Un átomo es la unidad básica de la materia que mantiene las propiedades de un elemento.",
                "domain": "chemistry",
            },
            {
                "question": "¿Qué es una molécula?",
                "choices": [
                    "Un átomo",
                    "Un grupo de átomos unidos",
                    "Un compuesto",
                    "Una reacción",
                ],
                "answer": 1,
                "explanation": "Una molécula es un grupo de átomos unidos por enlaces químicos.",
                "domain": "chemistryff",
            },
            {
                "question": "¿Qué es el pH?",
                "choices": [
                    "Una medida de temperatura",
                    "Una medida de acidez o basicidad",
                    "Una medida de presión",
                    "Una medida de volumen",
                ],
                "answer": 1,
                "explanation": "El pH es una medida de la acidez o basicidad de una solución acuosa.",
                "domain": "chemistry",
            },
            # BIOLOGÍA
            {
                "question": "¿Qué es la célula?",
                "choices": [
                    "Un tejido",
                    "La unidad básica de la vida",
                    "Un órgano",
                    "Un sistema",
                ],
                "answer": 1,
                "explanation": "La célula es la unidad básica de la vida, la estructura más pequeña capaz de realizar funciones vitales.",
                "domain": "biologyff",
            },
            {
                "question": "¿Qué es el ADN?",
                "choices": [
                    "Una proteína",
                    "El material genético",
                    "Una enzima",
                    "Una hormona",
                ],
                "answer": 1,
                "explanation": "El ADN es el material genético que contiene las instrucciones para el desarrollo y funcionamiento de los organismos.",
                "domain": "biology",
            },
            {
                "question": "¿Qué es la mitosis?",
                "choices": [
                    "Un tipo de respiración",
                    "Un tipo de división celular",
                    "Un tipo de digestión",
                    "Un tipo de reproducción",
                ],
                "answer": 1,
                "explanation": "La mitosis es un tipo de división celular que produce dos células hijas idénticas.",
                "domain": "biologyff",
            },
            {
                "question": "¿Qué es un ecosistema?",
                "choices": [
                    "Solo plantas",
                    "Una comunidad de organismos y su entorno",
                    "Solo animales",
                    "Solo bacterias",
                ],
                "answer": 1,
                "explanation": "Un ecosistema es una comunidad de organismos vivos y su entorno físico.",
                "domain": "biology",
            },
            {
                "question": "¿Qué es la homeostasis?",
                "choices": [
                    "Un tipo de enfermedad",
                    "El equilibrio interno del organismo",
                    "Un tipo de reproducción",
                    "Un tipo de evolución",
                ],
                "answer": 1,
                "explanation": "La homeostasis es el proceso mediante el cual los organismos mantienen un equilibrio interno estable.",
                "domain": "biology",
            },
        ],
        "testff": [
            # Preguntas de prueba adicionales
            {
                "question": "¿Cuál es el componente principal del aire?",
                "choices": ["Dióxido de carbono", "Nitrógeno", "Oxígeno", "Hidrógeno"],
                "answer": 1,
                "explanation": "El nitrógeno constituye aproximadamente el 78% del aire atmosférico.",
                "domain": "chemistry",
            },
            {
                "question": "¿Qué es la inteligencia artificial?",
                "choices": [
                    "Un tipo de computadora",
                    "Sistemas que simulan inteligencia humana",
                    "Un lenguaje de programación",
                    "Un algoritmo específico",
                ],
                "answer": 1,
                "explanation": "La IA se refiere a sistemas que pueden realizar tareas que requieren inteligencia humana.",
                "domain": "technicalff",
            },
            {
                "question": "¿Qué es la inflación?",
                "choices": [
                    "Un tipo de impuesto",
                    "El aumento general de precios",
                    "Un tipo de interés",
                    "Un tipo de cambio",
                ],
                "answer": 1,
                "explanation": "La inflación es el aumento general y sostenido de los precios de bienes y servicios.",
                "domain": "economics",
            },
            {
                "question": "¿Qué es la psicología?",
                "choices": [
                    "Solo el estudio de enfermedades mentales",
                    "El estudio científico del comportamiento y la mente",
                    "Solo el estudio del cerebro",
                    "Solo el estudio de emociones",
                ],
                "answer": 1,
                "explanation": "La psicología es el estudio científico del comportamiento humano y los procesos mentales.",
                "domain": "psychologyff",
            },
            {
                "question": "¿Qué es la ingeniería?",
                "choices": [
                    "Solo construcción",
                    "La aplicación de ciencia y matemáticas para resolver problemas",
                    "Solo diseño",
                    "Solo investigación",
                ],
                "answer": 1,
                "explanation": "La ingeniería es la aplicación de principios científicos y matemáticos para resolver problemas prácticos.",
                "domain": "engineering",
            },
        ],
    }

    return expanded_headqa


def convert_to_training_format(
    headqa_data: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Convert HEAD-QA dataset to training format"""
    training_data = []

    for split_name, questions in headqa_data.items():
        for q in questions:
            # Crear pregunta con opciones
            choices_text = [f"{i+1}. {choice}" for i, choice in enumerate(q["choices"])]

            # Respuesta correcta
            correct_answer = q["choices"][q["answer_idx"]]

            # Texto completo para entrenamiento
            explanation = q.get("explanation", "Sin explicación disponible")

            # Construir pregunta completa
            full_question = f"{q['question']}\n\n" + "\n".join(choices_text)
            full_answer = (
                f"Respuesta correcta: {correct_answer}\n\nExplicación: {explanation}"
            )

            training_data.append(
                {
                    "input_text": full_question,
                    "target_text": full_answer,
                    "quality_score": 0.95,
                    "source": f"headqa_expanded_{split_name}",
                    "timestamp": 1756062674.4658723,
                    "domain": q["domain"],
                }
            )

    return training_data


def main():
    """Función principal"""
    print("🚀 Expandiendo Dataset HEAD-QA")
    print("=" * 40)

    # Crear dataset expandido

    # Contar preguntas por dominio
    domain_counts = {}
    for split_name, questions in expanded_headqa.items():
        for q in questions:
            domain = q["domain"]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print(f"📊 Preguntas por dominio:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  🌿 {domain}: {count} preguntas")

    # Convertir a formato de entrenamiento

    # Guardar dataset expandido
    output_dir = Path("data/training_datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Guardar en formato HEAD-QA original
    with open(headqa_file, "w", encoding="utf-8") as f:
        json.dump(expanded_headqa, f, ensure_ascii=False, indent=2)

    # Guardar en formato de entrenamiento
    with open(training_file, "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Dataset HEAD-QA expandido creado:")
    print(f"  📁 Formato original: {headqa_file}")
    print(f"  📁 Formato entrenamiento: {training_file}")
    print(f"  📊 Total de preguntas: {len(training_data)}")
    print(f"  🌿 Dominios cubiertos: {len(domain_counts)}")

    # Mostrar estadísticas por split
    for split_name, questions in expanded_headqa.items():
        print(f"  📋 {split_name.capitalize()}: {len(questions)} preguntas")

    print(f"\n🎉 ¡Dataset HEAD-QA expandido exitosamente!")
    print(
        f"💡 Ahora tienes un dataset mucho más grande y variado para entrenar las ramas"
    )


if __name__ == "__main__":
    main()
