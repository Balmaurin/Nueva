#!/usr/bin/env python3
import os
import shutil
import json


class BranchStructureRestorer:
    """
    Restaurador de estructura original de ramas para Shaili-AI
    """

    def __init__(self, base_path="shaili-ai/branches"):
        """
        Inicializar restaurador de estructura de ramas

        Args:
            base_path (str): Ruta base de las ramas
        """
        self.base_path = base_path
        self.original_branches = [
            "arte,_música_y_cultura",
            "astronomía_y_espacio",
            "biología",
            "ciberseguridad_y_criptografía",
            "ciencia_de_datos_e_ia",
            "ciencias_de_la_tierra_y_clima",
            "cocina_y_nutrición",
            "computación_y_programación",
            "deportes_y_esports",
            "derecho_y_políticas_públicas",
            "diseño_y_ux",
            "economía_y_finanzas",
            "educación_y_pedagogía",
            "electrónica_y_iot",
            "empresa_y_emprendimiento",
            "física",
            "geografía_y_geo-política",
            "historia",
            "hogar,_diy_y_reparaciones",
            "ingeniería",
            "juegos_y_entretenimiento",
            "lengua_y_lingüística",
            "literatura_y_escritura",
            "matemáticas",
            "medicina_y_salud",
            "medios_y_comunicación",
            "neurociencia_y_psicología",
            "química",
            "sistemas_devops_redes",
            "sociología_y_antropología",
            "viajes_e_idiomas",
            "vida_diaria,_legal_práctico_y_trámites",
        ]

    def _create_branch_structure(self, branch_name):
        """
        Crear estructura de directorios para una rama

        Args:
            branch_name (str): Nombre de la rama
        """
        branch_path = os.path.join(self.base_path, branch_name)

        # Crear directorios
        os.makedirs(os.path.join(branch_path, "adapter"), exist_ok=True)
        os.makedirs(os.path.join(branch_path, "dataset"), exist_ok=True)

        # Crear README.md
        readme_path = os.path.join(branch_path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# Rama: {branch_name}\n\n")
                f.write("## Descripción\n")
                f.write(
                    f"Esta es la rama especializada para {branch_name} en el proyecto Shaili-AI.\n\n"
                )
                f.write("## Estructura\n")
                f.write("- `adapter/`: Adaptadores de modelo específicos del dominio\n")
                f.write(
                    "- `dataset/`: Conjuntos de datos para entrenamiento y fine-tuning\n"
                )

    def restore_branches(self):
        """
        Restaurar estructura de todas las ramas
        """
        print("Restaurando estructura de ramas...")

        # Crear estructura para cada rama
        for branch in self.original_branches:
            self._create_branch_structure(branch)
            print(f"Rama restaurada: {branch}")

        print("Restauración de ramas completada.")

    def validate_structure(self):
        """
        Validar la estructura de las ramas

        Returns:
            bool: True si la estructura es correcta, False en caso contrario
        """
        print("Validando estructura de ramas...")

        for branch in self.original_branches:
            branch_path = os.path.join(self.base_path, branch)

            # Verificar directorios
            adapter_path = os.path.join(branch_path, "adapter")
            dataset_path = os.path.join(branch_path, "dataset")
            readme_path = os.path.join(branch_path, "README.md")

            if not (
                os.path.isdir(adapter_path)
                and os.path.isdir(dataset_path)
                and os.path.isfile(readme_path)
            ):
                print(f"Error en estructura de rama: {branch}")
                return False

        print("Estructura de ramas validada correctamente.")
        return True


def main():
    """
    Ejecutar restauración de estructura de ramas
    """
    restorer = BranchStructureRestorer()

    try:
        # Restaurar ramas
        restorer.restore_branches()

        # Validar estructura
        if restorer.validate_structure():
            print("Restauración completada con éxito.")
        else:
            print("Error en la restauración de ramas.")

    except Exception as e:
        print(f"Error durante la restauración: {e}")


if __name__ == "__main__":
    main()
