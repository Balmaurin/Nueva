#!/usr/bin/env python3
import json
import os
import random

# Lista de dominios y subdominios para generar 32 ramas únicas
DOMAIN_CATEGORIES = [
    # Ciencias
    "Biología",
    "Física",
    "Química",
    "Astronomía",
    "Geología",
    "Ecología",
    "Neurociencia",
    "Genética",
    "Paleontología",
    "Oceanografía",
    # Tecnología
    "Inteligencia Artificial",
    "Ciberseguridad",
    "Desarrollo Web",
    "Redes",
    "Computación en la Nube",
    "Robótica",
    "Realidad Virtual",
    "Blockchain",
    "Internet de las Cosas",
    "Computación Cuántica",
    # Humanidades y Sociales
    "Historia",
    "Filosofía",
    "Antropología",
    "Psicología",
    "Sociología",
    "Arqueología",
    "Lingüística",
    "Estudios Culturales",
    "Ética",
    "Política",
    # Ramas adicionales para completar 32
    "Economía",
    "Artes Visuales",
]

BRANCH_NAMES = {
    "Biología": "Guardianes de la Vida",
    "Física": "Tejedores del Universo",
    "Química": "Alquimistas Modernos",
    "Astronomía": "Exploradores Cósmicos",
    "Geología": "Cronistas de la Tierra",
    "Ecología": "Defensores del Equilibrio",
    "Neurociencia": "Cartógrafos de la Mente",
    "Genética": "Arquitectos del ADN",
    "Paleontología": "Narradores de Eras Perdidas",
    "Oceanografía": "Navegantes de las Profundidades",
    "Inteligencia Artificial": "Pioneros de la Cognición Digital",
    "Ciberseguridad": "Centinelas Digitales",
    "Desarrollo Web": "Artesanos del Ciberespacio",
    "Redes": "Tejedores de Conexiones",
    "Computación en la Nube": "Constructores de Nubes Digitales",
    "Robótica": "Creadores de Autómatas",
    "Realidad Virtual": "Arquitectos de Mundos Imaginarios",
    "Blockchain": "Forjadores de Confianza Digital",
    "Internet de las Cosas": "Sinfonistas de la Tecnología Conectada",
    "Computación Cuántica": "Visionarios de la Mecánicá Cuántica",
    "Historia": "Cronistas de la Memoria Colectiva",
    "Filosofía": "Buscadores de la Sabiduría Eterna",
    "Antropología": "Intérpretes de la Humanidad",
    "Psicología": "Exploradores del Alma Humana",
    "Sociología": "Tejedores de Relaciones Sociales",
    "Arqueología": "Descifradores de Civilizaciones",
    "Lingüística": "Arquitectos del Lenguaje",
    "Estudios Culturales": "Puentes Entre Mundos",
    "Ética": "Guardianes de los Principios",
    "Política": "Constructores de Sociedades",
    "Economía": "Estrategas de los Recursos",
    "Artes Visuales": "Alquimistas de la Percepción",
}


def generate_example(domain):
    """Generar un ejemplo de entrenamiento para un dominio específico"""
    instructions = [
        f"Explica un concepto fundamental en {domain}",
        f"Describe un método o técnico importante en {domain}",
        f"Proporciona una visión general de {domain}",
        f"Discute un tema de actualidad en {domain}",
    ]

    instruction = random.choice(instructions)

    # Ejemplos de respuestas generadas dinámicamente
    responses = [
        f"{domain} es un campo fascinante que estudia {random.choice(['fenómenos', 'procesos', 'sistemas'])} complejos.",
        f"Los principios fundamentales de {domain} incluyen conceptos como {random.choice(['innovación', 'investigación', 'análisis', 'comprensión'])}.",
        f"El desarrollo reciente en {domain} ha revolucionado nuestra comprensión de {random.choice(['la realidad', 'los sistemas', 'la información', 'el conocimiento'])}.",
        f"Las técnicas avanzadas en {domain} permiten {random.choice(['resolver problemas', 'explorar nuevas fronteras', 'comprender fenómenos complejos', 'innovar'])}.",
    ]

    return {"instruction": instruction, "input": "", "output": random.choice(responses)}


def generate_datasets():
    """Generar archivos de dataset para 32 ramas"""
    base_path = "/home/yo/Escritorio/DEFINITIVO (Copiar 3)/sheily-ai/data/branches"
    models_path = (
        "/home/yo/Escritorio/DEFINITIVO (Copiar 3)/sheily-ai/models/qwen_branches"
    )

    # Asegurar directorios
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(models_path, exist_ok=True)

    # Generar configuración de ramas
    branch_config = {}

    # Generar 32 ramas
    for i, domain in enumerate(DOMAIN_CATEGORIES, 1):
        # Crear dataset para cada rama
        dataset_path = os.path.join(base_path, f"branch_{i:02d}_dataset.jsonl")
        branch_name = f"branch_{i:02d}"
        branch_output_path = os.path.join(models_path, branch_name)

        # Crear directorio para el modelo de rama
        os.makedirs(branch_output_path, exist_ok=True)

        # Generar ejemplos para el dataset
        examples = [generate_example(domain) for _ in range(5)]  # 5 ejemplos por rama

        # Guardar dataset
        with open(dataset_path, "w", encoding="utf-8") as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")

        # Configuración de la rama
        branch_config[branch_name] = {
            "name": BRANCH_NAMES[domain],
            "dataset_path": dataset_path,
            "output_path": branch_output_path,
            "training_steps": 1500,
            "keywords": [domain.lower()],
        }

        print(
            f"Dataset generado para rama {branch_name} ({BRANCH_NAMES[domain]}): {dataset_path}"
        )

    # Guardar configuración de ramas
    config_path = (
        "/home/yo/Escritorio/DEFINITIVO (Copiar 3)/sheily-ai/config/branch_config.json"
    )
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(branch_config, f, indent=2, ensure_ascii=False)

    print(f"\nConfiguraciones de ramas guardadas en: {config_path}")


def main():
    generate_datasets()


if __name__ == "__main__":
    main()
