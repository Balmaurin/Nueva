#!/usr/bin/env python3
"""
Script para importar datasets de entrenamiento a la base de datos por ramas
"""

from core.branch_training_database import (
    get_branch_training_database,
)
import json
from pathlib import Path
import sys

# Agregar el directorio ai al path
sys.path.append(str(Path(__file__).parent / "ai"))


def create_synthetic_branch_datasets():
    """Crear datasets sintéticos específicos para cada rama"""
    print("🔄 Creando datasets sintéticos por ramas...")

    # Datasets sintéticos organizados por ramas
    branch_datasets = {
        "medical": [
            {
                "input_text": "¿Cuáles son los síntomas principales del COVID-19?",
                "target_text": "Los síntomas principales del COVID-19 incluyen fiebre, tos seca, fatiga, pérdida del gusto u olfato, dificultad para respirar, dolor muscular y de garganta. En casos graves puede causar neumonía y síndrome de dificultad respiratoria aguda.",
                "quality_score": 0.95,
                "source": "synthetic_medical",
                "domain": "medical",
            },
            {
                "input_text": "¿Qué es la hipertensión arterial?",
                "target_text": "La hipertensión arterial es una condición médica caracterizada por una presión arterial persistentemente elevada. Se considera hipertensión cuando la presión sistólica es ≥140 mmHg y/o la diastólica ≥90 mmHg. Es un factor de riesgo importante para enfermedades cardiovasculares.",
                "quality_score": 0.95,
                "source": "synthetic_medical",
                "domain": "medical",
            },
            {
                "input_text": "¿Cuáles son las medidas de prevención del COVID-19?",
                "target_text": "Las medidas de prevención incluyen lavado frecuente de manos, uso de mascarilla, distanciamiento social, ventilación de espacios, vacunación y evitar aglomeraciones. Estas medidas reducen significativamente el riesgo de contagio.",
                "quality_score": 0.95,
                "source": "synthetic_medical",
                "domain": "medical",
            },
        ],
        "technicalff": [
            {
                "input_text": "¿Qué es el machine learning?",
                "target_text": "El machine learning es una rama de la inteligencia artificial que permite a las computadoras aprender y mejorar automáticamente a partir de la experiencia sin ser programadas explícitamente. Utiliza algoritmos que identifican patrones en datos para hacer predicciones o decisiones.",
                "quality_score": 0.95,
                "source": "synthetic_technical",
                "domain": "technical",
            },
            {
                "input_text": "¿Cómo funciona una red neuronal?",
                "target_text": "Una red neuronal es un modelo computacional inspirado en el cerebro humano. Consiste en capas de nodos interconectados que procesan información. Cada conexión tiene un peso que se ajusta durante el entrenamiento para minimizar el error en las predicciones.",
                "quality_score": 0.95,
                "source": "synthetic_technical",
                "domain": "technicalff",
            },
            {
                "input_text": "¿Cuáles son los tipos principales de machine learning?",
                "target_text": "Los tipos principales son: aprendizaje supervisado (con datos etiquetados), no supervisado (sin etiquetas), semi-supervisado (mezcla de ambos) y por refuerzo (aprendizaje basado en recompensas). Cada tipo se aplica según el problema específico.",
                "quality_score": 0.95,
                "source": "synthetic_technical",
                "domain": "technical",
            },
        ],
        "legalff": [
            {
                "input_text": "¿Qué es el derecho constitucional?",
                "target_text": "El derecho constitucional es la rama del derecho público que estudia la organización y funcionamiento del Estado, los derechos fundamentales de las personas y las garantías constitucionales. Se basa en la Constitución como norma suprema del ordenamiento jurídico.",
                "quality_score": 0.95,
                "source": "synthetic_legal",
                "domain": "legal",
            },
            {
                "input_text": "¿Cuáles son los derechos fundamentales?",
                "target_text": "Los derechos fundamentales son aquellos derechos humanos reconocidos y protegidos por la Constitución. Incluyen derechos como la vida, libertad, igualdad, propiedad, educación, salud, trabajo, y otros que garantizan la dignidad humana y el desarrollo integral de la persona.",
                "quality_score": 0.95,
                "source": "synthetic_legal",
                "domain": "legal",
            },
        ],
        "scientificff": [
            {
                "input_text": "¿Qué es la teoría de la evolución?",
                "target_text": "La teoría de la evolución propuesta por Charles Darwin explica cómo las especies cambian a lo largo del tiempo mediante el proceso de selección natural. Los individuos con características ventajosas tienen mayor probabilidad de sobrevivir y reproducirse, transmitiendo sus genes a la siguiente generación.",
                "quality_score": 0.95,
                "source": "synthetic_scientific",
                "domain": "scientific",
            },
            {
                "input_text": "¿Cómo funciona la fotosíntesis?",
                "target_text": "La fotosíntesis es el proceso mediante el cual las plantas, algas y algunas bacterias convierten la energía solar en energía química. Utilizan dióxido de carbono y agua para producir glucosa y oxígeno, liberando este último a la atmósfera como subproducto.",
                "quality_score": 0.95,
                "source": "synthetic_scientific",
                "domain": "scientific",
            },
        ],
        "businessff": [
            {
                "input_text": "¿Qué es el marketing digital?",
                "target_text": "El marketing digital es el conjunto de estrategias publicitarias y comerciales que se ejecutan en medios y canales de internet. Incluye SEO, SEM, redes sociales, email marketing, content marketing y otras técnicas para promocionar productos o servicios en el entorno digital.",
                "quality_score": 0.95,
                "source": "synthetic_business",
                "domain": "business",
            },
            {
                "input_text": "¿Cómo funciona la economía de mercado?",
                "target_text": "La economía de mercado es un sistema económico donde las decisiones de producción, distribución y consumo están determinadas por la oferta y demanda. Los precios se establecen libremente en el mercado, y la competencia entre empresas regula la eficiencia y calidad de los productos.",
                "quality_score": 0.95,
                "source": "synthetic_business",
                "domain": "business",
            },
        ],
        "programmingff": [
            {
                "input_text": "¿Qué es Python y para qué se usa?",
                "target_text": "Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. Se caracteriza por su sintaxis simple y legible. Se usa para desarrollo web, análisis de datos, inteligencia artificial, automatización, y muchas otras aplicaciones.",
                "quality_score": 0.95,
                "source": "synthetic_programming",
                "domain": "programming",
            },
            {
                "input_text": "¿Qué es un algoritmo?",
                "target_text": "Un algoritmo es una secuencia finita de instrucciones bien definidas para resolver un problema específico. Es como una receta que describe paso a paso cómo realizar una tarea. Los algoritmos son fundamentales en programación y ciencias de la computación.",
                "quality_score": 0.95,
                "source": "synthetic_programming",
                "domain": "programming",
            },
        ],
        "mathematicsff": [
            {
                "input_text": "¿Qué es el cálculo diferencial?",
                "target_text": "El cálculo diferencial es una rama de las matemáticas que estudia las tasas de cambio instantáneas. Se basa en el concepto de derivada, que mide cómo cambia una función en un punto específico. Es fundamental en física, ingeniería y muchas otras ciencias.",
                "quality_score": 0.95,
                "source": "synthetic_mathematics",
                "domain": "mathematics",
            },
            {
                "input_text": "¿Qué son las ecuaciones cuadráticas?",
                "target_text": "Las ecuaciones cuadráticas son ecuaciones polinómicas de segundo grado que tienen la forma ax² + bx + c = 0. Se pueden resolver usando la fórmula cuadrática, completando el cuadrado, o factorizando. Tienen aplicaciones en física, ingeniería y economía.",
                "quality_score": 0.95,
                "source": "synthetic_mathematics",
                "domain": "mathematics",
            },
        ],
        "physicsff": [
            {
                "input_text": "¿Qué es la ley de gravitación universal?",
                "target_text": "La ley de gravitación universal de Newton establece que dos cuerpos se atraen con una fuerza proporcional al producto de sus masas e inversamente proporcional al cuadrado de la distancia entre ellos. Esta ley explica el movimiento de los planetas y muchos otros fenómenos astronómicos.",
                "quality_score": 0.95,
                "source": "synthetic_physics",
                "domain": "physics",
            },
            {
                "input_text": "¿Qué es la energía cinética?",
                "target_text": "La energía cinética es la energía que posee un objeto debido a su movimiento. Se calcula como E = ½mv², donde m es la masa del objeto y v es su velocidad. Es una forma fundamental de energía que se puede convertir en otras formas.",
                "quality_score": 0.95,
                "source": "synthetic_physics",
                "domain": "physics",
            },
        ],
        "chemistryff": [
            {
                "input_text": "¿Qué es una reacción química?",
                "target_text": "Una reacción química es un proceso donde las sustancias (reactivos) se transforman en nuevas sustancias (productos) mediante la ruptura y formación de enlaces químicos. Las reacciones químicas siguen la ley de conservación de la masa y pueden liberar o absorber energía.",
                "quality_score": 0.95,
                "source": "synthetic_chemistry",
                "domain": "chemistry",
            },
            {
                "input_text": "¿Qué es la tabla periódica?",
                "target_text": "La tabla periódica es una organización sistemática de los elementos químicos ordenados por su número atómico. Los elementos están agrupados en períodos (filas) y grupos (columnas) según sus propiedades químicas y electrónicas. Fue desarrollada por Dmitri Mendeleev.",
                "quality_score": 0.95,
                "source": "synthetic_chemistry",
                "domain": "chemistry",
            },
        ],
        "biologyff": [
            {
                "input_text": "¿Qué es la célula?",
                "target_text": "La célula es la unidad básica de la vida. Es la estructura más pequeña capaz de realizar todas las funciones vitales: nutrición, relación y reproducción. Las células pueden ser procariotas (sin núcleo) o eucariotas (con núcleo). Todos los seres vivos están formados por células.",
                "quality_score": 0.95,
                "source": "synthetic_biology",
                "domain": "biology",
            },
            {
                "input_text": "¿Qué es la fotosíntesis?",
                "target_text": "La fotosíntesis es el proceso mediante el cual las plantas, algas y algunas bacterias convierten la energía solar en energía química. Utilizan dióxido de carbono y agua para producir glucosa y oxígeno, liberando este último a la atmósfera como subproducto.",
                "quality_score": 0.95,
                "source": "synthetic_biology",
                "domain": "biology",
            },
        ],
    }

    # Guardar datasets por ramas
    output_dir = Path("data/training_datasets/branches")
    output_dir.mkdir(parents=True, exist_ok=True)

    total_examples = 0
    for branch_name, examples in branch_datasets.items():
        output_file = output_dir / f"{branch_name}_dataset.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)

        print(f"✅ Rama '{branch_name}': {len(examples)} ejemplos")
        total_examples += len(examples)

    print(f"📊 Total de ejemplos sintéticos creados: {total_examples}")
    return output_dir


def import_datasets_to_branches():
    """Importar todos los datasets a la base de datos por ramas"""
    print("🚀 Iniciando importación de datasets a ramas...")

    # Obtener instancia de la base de datos
    db = get_branch_training_database()

    # Directorio de datasets

    if not datasets_dir.exists():
        print("Datasets directory not found")
        return

    total_imported = 0

    # Importar datasets existentes
    for json_file in datasets_dir.glob("*.json"):
        if json_file.name != "branches":  # Excluir directorio
            print(f"🔄 Importando: {json_file.name}")

            try:
                imported_count = db.import_from_json(
                    str(json_file), source=f"imported_{json_file.stem}"
                )
                total_imported += imported_count
                print(f"  ✅ Importados: {imported_count} ejemplos")

            except Exception as e:
                print(f"  ❌ Error importando {json_file.name}: {e}")

    # Importar datasets por ramas
    if branches_dir.exists():
        print(f"\n🔄 Importando datasets específicos por ramas...")

        for json_file in branches_dir.glob("*.json"):
            branch_name = json_file.stem
            print(f"🔄 Importando rama: {branch_name}")

            try:
                imported_count = db.import_from_json(
                    str(json_file), source=f"branch_{branch_name}"
                )
                total_imported += imported_count
                print(f"  ✅ Rama '{branch_name}': {imported_count} ejemplos")

            except Exception as e:
                print(f"  ❌ Error importando rama {branch_name}: {e}")

    print(f"\n🎉 Importación completada!")
    print(f"📊 Total de ejemplos importados: {total_imported}")

    # Mostrar estadísticas por ramas
    print(f"\n📈 Estadísticas por ramas:")

    for branch_name, branch_stats in stats.items():
        if branch_stats["total_examples"] > 0:
            print(
                f"  🌿 {branch_stats['display_name']}: {branch_stats['total_examples']} ejemplos (calidad: {branch_stats['avg_quality_score']:.2f})"
            )

            return total_imported


def test_branch_classification():
    """Probar la clasificación automática de ejemplos"""
    print("🧪 Probando clasificación automática de ramas...")

    db = get_branch_training_database()

    test_examples = [
        (
            "¿Cuáles son los síntomas del COVID-19?",
            "Los síntomas incluyen fiebre, tos y fatiga...",
        ),
        ("¿Qué es Python?", "Python es un lenguaje de programación..."),
        (
            "¿Qué es la ley de gravitación?",
            "La ley de gravitación universal establece...",
        ),
        (
            "¿Cómo funciona el marketing digital?",
            "El marketing digital incluye estrategias...",
        ),
        (
            "¿Qué es una ecuación cuadrática?",
            "Una ecuación cuadrática tiene la forma ax² + bx + c = 0...",
        ),
    ]

    for question, answer in test_examples:
        print(f"  ❓ '{question[:50]}...' → 🌿 Rama: {branch}")

    print("✅ Prueba de clasificación completada")


def main():
    """Función principal"""
    print("🚀 Sistema de Importación de Datasets por Ramas")
    print("=" * 50)

    # Crear datasets sintéticos por ramas
    create_synthetic_branch_datasets()

    # Importar todos los datasets
    import_datasets_to_branches()

    # Probar clasificación
    test_branch_classification()

    print(f"\n🎉 ¡Proceso completado exitosamente!")
    print(f"📂 Los datos están organizados en la base de datos por ramas")
    print(f"💡 Cada rama puede entrenarse independientemente")
    # Nota: total_imported no está disponible aquí, se calcula dentro de import_datasets_to_branches()


if __name__ == "__main__":
    main()
