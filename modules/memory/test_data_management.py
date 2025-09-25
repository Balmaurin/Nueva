#!/usr/bin/env python3
"""
Script de prueba para el módulo de gestión de datos
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from modules.memory.data_management import DataManagementService
import json
import tempfile
import shutil


def test_data_management():
    """Prueba el módulo de gestión de datos"""
    print("🧪 Probando módulo de gestión de datos...")

    # Crear directorio temporal para pruebas
    test_dir = tempfile.mkdtemp()
    db_path = os.path.join(test_dir, "test_user_data.duckdb")
    log_dir = os.path.join(test_dir, "logs")

    try:
        # Crear instancia del servicio
        service = DataManagementService(db_path=db_path, log_dir=log_dir)

        # Datos de prueba
        test_user_id = "user_123"
        test_data = {
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "preferences": {"language": "es", "theme": "dark"},
        }

        print(f"👤 Usuario de prueba: {test_user_id}")
        print(
            f"📊 Datos de prueba: {json.dumps(test_data, indent=2, ensure_ascii=False)}"
        )

        # Probar almacenamiento de datos
        print("\n💾 Almacenando datos...")
        service.store_user_data(
            user_id=test_user_id,
            data=test_data,
            domain="user_profile",
            data_type="profile",
            is_pii=True,
            retention_period=365,
        )

        # Probar almacenamiento de datos no PII
        print("\n💾 Almacenando datos no PII...")
        service.store_user_data(
            user_id=test_user_id,
            data={"last_login": "2024-01-15", "session_count": 5},
            domain="analytics",
            data_type="session",
            is_pii=False,
            retention_period=30,
        )

        # Probar exportación de datos
        print("\n📤 Exportando datos...")
        export_path = service.export_user_data(test_user_id, "jsonl")
        print(f"Archivo exportado: {export_path}")

        # Verificar contenido del archivo exportado
        if os.path.exists(export_path):
            with open(export_path, "r", encoding="utf-8") as f:
                exported_data = [json.loads(line) for line in f]
            print(f"Datos exportados: {len(exported_data)} registros")
            for entry in exported_data:
                print(f"  - {entry['domain']}/{entry['data_type']}: {entry['is_pii']}")

        # Probar borrado selectivo
        print("\n🗑️ Borrando datos de analytics...")
        deleted_count = service.delete_user_data(
            user_id=test_user_id,
            domain="analytics",
            reason="Prueba de borrado selectivo",
        )
        print(f"Registros eliminados: {deleted_count}")

        # Probar limpieza de datos expirados
        print("\n🧹 Limpiando datos expirados...")
        cleaned_count = service.cleanup_expired_data()
        print(f"Registros expirados eliminados: {cleaned_count}")

        print("\n✅ Pruebas completadas exitosamente!")

    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        raise
    finally:
        # Limpiar archivos temporales
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print(f"🧹 Directorio temporal eliminado: {test_dir}")


if __name__ == "__main__":
    test_data_management()
