#!/usr/bin/env python3
import json
import random


def select_representative_branches(
    input_file="shaili-ai/branches/base_branches.json", num_branches=32
):
    """
    Seleccionar micro-ramas representativas de manera estratégica

    Args:
        input_file (str): Ruta al archivo JSON de ramas
        num_branches (int): Número de ramas a seleccionar

    Returns:
        dict: Diccionario de ramas seleccionadas
    """
    # Cargar ramas originales
    with open(input_file, "r", encoding="utf-8") as f:
        original_branches = json.load(f)

    # Estrategia de selección
    selected_branches = {}

    # Calcular número de ramas por dominio
    domains = list(original_branches.keys())
    branches_per_domain = {domain: len(original_branches[domain]) for domain in domains}
    total_original_branches = sum(branches_per_domain.values())

    # Calcular distribución proporcional
    for domain in domains:
        # Calcular número de ramas para este dominio
        domain_branches = original_branches[domain]
        domain_proportion = len(domain_branches) / total_original_branches
        domain_branch_count = max(1, round(domain_proportion * num_branches))

        # Seleccionar ramas representativas de forma determinística
        selected_domain_branches = domain_branches[
            : min(domain_branch_count, len(domain_branches))
        ]
        selected_branches[domain] = selected_domain_branches

    # Ajustar para llegar exactamente a 32
    current_total = sum(len(branches) for branches in selected_branches.values())

    # Si hay menos de 32, añadir más ramas
    while current_total < num_branches:
        for domain in domains:
            if current_total < num_branches:
                remaining_branches = set(original_branches[domain]) - set(
                    selected_branches[domain]
                )
                if remaining_branches:
                    # Selección determinística del primer elemento disponible
                    remaining_list = list(remaining_branches)
                    new_branch = remaining_list[0]
                    selected_branches[domain].append(new_branch)
                    current_total += 1

    # Si hay más de 32, eliminar algunas
    while current_total > num_branches:
        for domain in domains:
            if current_total > num_branches and len(selected_branches[domain]) > 1:
                selected_branches[domain].pop()
                current_total -= 1

    return selected_branches


def main():
    """
    Ejecutar selección de ramas y guardar resultado
    """
    # Seleccionar 32 ramas
    selected_branches = select_representative_branches()

    # Imprimir resultado
    print("Ramas seleccionadas:")
    for domain, branches in selected_branches.items():
        print(f"\n{domain} ({len(branches)} ramas):")
        for branch in branches:
            print(f"- {branch}")

    # Contar total de ramas
    total_branches = sum(len(branches) for branches in selected_branches.values())
    print(f"\nTotal de ramas seleccionadas: {total_branches}")

    # Guardar resultado
    output_file = "shaili-ai/branches/selected_branches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(selected_branches, f, ensure_ascii=False, indent=4)

    print(f"\nRamas guardadas en {output_file}")


if __name__ == "__main__":
    main()
