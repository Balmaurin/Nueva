import os
import sys
import secrets
import argparse
import json
from dotenv import load_dotenv, set_key


class EnvManager:
    def __init__(self, env_path=".env"):
        """
        Inicializar gestor de entorno

        Args:
            env_path (str): Ruta del archivo de entorno
        """
        self.env_path = env_path
        load_dotenv(env_path)

    def generate_secret_key(self, length=64):
        """
        Generar clave secreta segura

        Args:
            length (int): Longitud de la clave

        Returns:
            str: Clave secreta generada
        """
        return secrets.token_hex(length // 2)

    def set_environment(self, key, value):
        """
        Establecer variable de entorno

        Args:
            key (str): Nombre de la variable
            value (str): Valor de la variable
        """
        try:
            set_key(self.env_path, key, str(value))
            print(f"✅ Variable {key} establecida correctamente.")
        except Exception as e:
            print(f"❌ Error estableciendo {key}: {e}")

    def generate_secure_config(self):
        """
        Generar configuración segura por defecto
        """
        secure_config = {
            "SECRET_KEY": self.generate_secret_key(),
            "POSTGRES_PASSWORD": secrets.token_urlsafe(16),
            "REDIS_PASSWORD": secrets.token_urlsafe(16),
            "GRAFANA_ADMIN_PASSWORD": secrets.token_urlsafe(16),
        }

        for key, value in secure_config.items():
            self.set_environment(key, value)

        print("🔒 Configuración segura generada.")

    def validate_config(self):
        """
        Validar configuración de entorno

        Returns:
            dict: Resultados de validación
        """
        validation_results = {
            "secret_key": len(os.getenv("SECRET_KEY", "")) >= 64,
            "postgres_config": all(
                [
                    os.getenv("POSTGRES_HOST"),
                    os.getenv("POSTGRES_USER"),
                    os.getenv("POSTGRES_PASSWORD"),
                ]
            ),
            "redis_config": all([os.getenv("REDIS_HOST"), os.getenv("REDIS_PASSWORD")]),
        }

        return validation_results

    def export_config(self, format="json"):
        """
        Exportar configuración

        Args:
            format (str): Formato de exportación

        Returns:
            str: Configuración exportada
        """
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("_")}

        if format == "json":
            return json.dumps(env_vars, indent=2)
        elif format == "env":
            return "\n".join([f"{k}={v}" for k, v in env_vars.items()])
        else:
            raise ValueError("Formato no soportado")


def main():
    parser = argparse.ArgumentParser(description="Gestor de Entorno Shaili-AI")
    parser.add_argument(
        "--generate-secrets", action="store_true", help="Generar claves secretas"
    )
    parser.add_argument("--validate", action="store_true", help="Validar configuración")
    parser.add_argument(
        "--export", choices=["json", "env"], help="Exportar configuración"
    )
    parser.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Establecer variable de entorno",
    )

    args = parser.parse_args()
    env_manager = EnvManager()

    if args.generate_secrets:
        env_manager.generate_secure_config()

    if args.validate:
        validation = env_manager.validate_config()
        print(json.dumps(validation, indent=2))

    if args.export:
        print(env_manager.export_config(args.export))

    if args.set:
        env_manager.set_environment(args.set[0], args.set[1])


if __name__ == "__main__":
    main()
