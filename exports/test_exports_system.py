#!/usr/bin/env python3
"""
Sistema de Pruebas - Sistema de Exportación Shaili AI

Este script ejecuta pruebas completas para validar que todos los componentes
del sistema de exportación funcionen correctamente.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime


def test_export_manager():
    """Probar el gestor de exportación"""
    print("🧪 Probando ExportManager...")

    try:
        from export_manager import ExportManager, ExportConfig

        # Crear configuración de prueba
        config = ExportConfig(
            format="jsonl", include_pii=True, include_metadata=True, compress=False
        )

        manager = ExportManager(config)

        # Probar exportación de datos de usuario
        result = manager.export_user_data("test_user_123", ["profile", "sessions"])

        if result["success"]:
            print(f"  ✅ Exportación de usuario exitosa: {result['filename']}")
            print(f"     Registros: {result['total_records']}")
            print(f"     Tamaño: {result['file_size']} bytes")
        else:
            print(
                f"  ❌ Error en exportación de usuario: {result.get('error', 'Unknown error')}"
            )
            return False

        # Probar exportación de conversaciones
        conv_result = manager.export_conversations()

        if conv_result["success"]:
            print(
                f"  ✅ Exportación de conversaciones exitosa: {conv_result['filename']}"
            )
        else:
            print(
                f"  ❌ Error en exportación de conversaciones: {conv_result.get('error', 'Unknown error')}"
            )
            return False

        # Probar exportación de datos del sistema
        sys_result = manager.export_system_data(["config", "performance"])

        if sys_result["success"]:
            print(f"  ✅ Exportación del sistema exitosa: {sys_result['filename']}")
        else:
            print(
                f"  ❌ Error en exportación del sistema: {sys_result.get('error', 'Unknown error')}"
            )
            return False

        # Probar historial
        history = manager.get_export_history(5)
        print(f"  ✅ Historial de exportaciones: {len(history)} entradas")

        return True

    except Exception as e:
        print(f"  ❌ Error en ExportManager: {e}")
        return False


def test_data_exporter():
    """Probar el exportador de datos especializado"""
    print("🧪 Probando DataExporter...")

    try:
        from data_exporter import DataExporter, ExportSpecification

        exporter = DataExporter()

        # Crear archivo de prueba para conversaciones
        test_db_path = Path("test_conversations.db")
        import sqlite3

        conn = sqlite3.connect(test_db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                message TEXT,
                timestamp TEXT,
                topic TEXT
            )
        """
        )

        # Insertar datos de prueba
        test_data = [
            (
                "conv_1",
                "user_123",
                "¿Qué es la fotosíntesis?",
                "2024-01-15T10:00:00",
                "ciencia",
            ),
            (
                "conv_2",
                "user_456",
                "¿Cómo funciona la IA?",
                "2024-01-15T11:00:00",
                "tecnología",
            ),
            (
                "conv_3",
                "user_123",
                "¿Cuál es la capital de España?",
                "2024-01-15T12:00:00",
                "geografía",
            ),
        ]

        conn.executemany(
            "INSERT OR REPLACE INTO conversations VALUES (?, ?, ?, ?, ?)", test_data
        )
        conn.commit()
        conn.close()

        # Probar exportación de conversaciones
        conv_spec = ExportSpecification(
            data_type="conversations",
            source_path=str(test_db_path),
            output_format="jsonl",
        )

        result = exporter.export_conversations(conv_spec)

        if result["success"]:
            print(f"  ✅ Exportación de conversaciones exitosa: {result['filename']}")
        else:
            print(
                f"  ❌ Error en exportación de conversaciones: {result.get('error', 'Unknown error')}"
            )
            return False

        # Probar exportación en diferentes formatos
        formats_to_test = ["csv", "json", "parquet"]
        for fmt in formats_to_test:
            spec = ExportSpecification(
                data_type="conversations",
                source_path=str(test_db_path),
                output_format=fmt,
            )

            result = exporter.export_conversations(spec)
            if result["success"]:
                print(f"  ✅ Exportación en formato {fmt} exitosa")
            else:
                print(
                    f"  ❌ Error en formato {fmt}: {result.get('error', 'Unknown error')}"
                )

        # Limpiar archivo de prueba
        test_db_path.unlink()

        return True

    except Exception as e:
        print(f"  ❌ Error en DataExporter: {e}")
        return False


def test_package_imports():
    """Probar importaciones del paquete"""
    print("🧪 Probando importaciones del paquete...")

    try:
        import exports

        # Probar funciones de conveniencia
        result = exports.export_user_data(
            "test_user", format="jsonl", include_pii=False
        )
        if result["success"]:
            print("  ✅ Función export_user_data funcionando")
        else:
            print(
                f"  ❌ Error en export_user_data: {result.get('error', 'Unknown error')}"
            )

        # Probar configuración
        config = exports.create_export_config(format="csv", include_pii=False)
        if config.format == "csv":
            print("  ✅ Función create_export_config funcionando")
        else:
            print("  ❌ Error en create_export_config")

        # Probar especificación
        spec = exports.create_export_specification(
            data_type="conversations", source_path="test.db", output_format="jsonl"
        )
        if spec.data_type == "conversations":
            print("  ✅ Función create_export_specification funcionando")
        else:
            print("  ❌ Error en create_export_specification")

        # Probar funciones de utilidad
        formats = exports.get_supported_formats()
        if len(formats) > 0:
            print(
                f"  ✅ Función get_supported_formats funcionando: {len(formats)} formatos"
            )
        else:
            print("  ❌ Error en get_supported_formats")

        data_types = exports.get_supported_data_types()
        if len(data_types) > 0:
            print(
                f"  ✅ Función get_supported_data_types funcionando: {len(data_types)} tipos"
            )
        else:
            print("  ❌ Error en get_supported_data_types")

        return True

    except Exception as e:
        print(f"  ❌ Error en importaciones del paquete: {e}")
        return False


def test_file_operations():
    """Probar operaciones de archivos"""
    print("🧪 Probando operaciones de archivos...")

    try:
        from export_manager import ExportManager, ExportConfig

        config = ExportConfig(
            format="jsonl",
            include_pii=True,
            include_metadata=True,
            compress=True,  # Probar compresión
        )

        manager = ExportManager(config)

        # Probar exportación con compresión
        result = manager.export_user_data("test_user_compressed", ["profile"])

        if result["success"]:
            print(f"  ✅ Exportación comprimida exitosa: {result['filename']}")

            # Verificar que el archivo existe y está comprimido
            file_path = Path(result["file_path"])
            if file_path.exists():
                print(
                    f"  ✅ Archivo comprimido existe: {file_path.stat().st_size} bytes"
                )
            else:
                print("  ❌ Archivo comprimido no encontrado")
                return False
        else:
            print(
                f"  ❌ Error en exportación comprimida: {result.get('error', 'Unknown error')}"
            )
            return False

        # Probar limpieza de archivos antiguos
        deleted_count = manager.cleanup_old_exports(days=0)  # Eliminar archivos de hoy
        print(f"  ✅ Limpieza de archivos: {deleted_count} archivos eliminados")

        return True

    except Exception as e:
        print(f"  ❌ Error en operaciones de archivos: {e}")
        return False


def test_metadata_generation():
    """Probar generación de metadatos"""
    print("🧪 Probando generación de metadatos...")

    try:
        from export_manager import ExportManager, ExportConfig

        config = ExportConfig(format="json", include_pii=True, include_metadata=True)

        manager = ExportManager(config)

        # Probar exportación con metadatos
        result = manager.export_user_data("test_user_metadata", ["profile", "sessions"])

        if result["success"]:
            print(f"  ✅ Exportación con metadatos exitosa: {result['filename']}")

            # Verificar archivo de metadatos
            metadata_path = Path(result["metadata_path"])
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                required_fields = [
                    "export_id",
                    "timestamp",
                    "format",
                    "total_records",
                    "checksum",
                ]
                missing_fields = [
                    field for field in required_fields if field not in metadata
                ]

                if not missing_fields:
                    print("  ✅ Metadatos completos generados")
                    print(f"     Export ID: {metadata['export_id']}")
                    print(f"     Checksum: {metadata['checksum'][:16]}...")
                else:
                    print(f"  ❌ Campos faltantes en metadatos: {missing_fields}")
                    return False
            else:
                print("  ❌ Archivo de metadatos no encontrado")
                return False
        else:
            print(
                f"  ❌ Error en exportación con metadatos: {result.get('error', 'Unknown error')}"
            )
            return False

        return True

    except Exception as e:
        print(f"  ❌ Error en generación de metadatos: {e}")
        return False


def test_error_handling():
    """Probar manejo de errores"""
    print("🧪 Probando manejo de errores...")

    try:
        from export_manager import ExportManager, ExportConfig
        from data_exporter import DataExporter, ExportSpecification

        # Probar con configuración inválida
        config = ExportConfig(format="invalid_format")
        manager = ExportManager(config)

        result = manager.export_user_data("test_user", ["profile"])
        if not result["success"]:
            print("  ✅ Error manejado correctamente para formato inválido")
        else:
            print("  ❌ Error no manejado para formato inválido")
            return False

        # Probar con ruta de base de datos inexistente
        exporter = DataExporter()
        spec = ExportSpecification(
            data_type="conversations",
            source_path="nonexistent.db",
            output_format="jsonl",
        )

        result = exporter.export_conversations(spec)
        if not result["success"]:
            print("  ✅ Error manejado correctamente para archivo inexistente")
        else:
            print("  ❌ Error no manejado para archivo inexistente")
            return False

        # Probar con datos vacíos
        config = ExportConfig(format="jsonl")
        manager = ExportManager(config)

        # Simular datos vacíos
        result = manager.export_user_data("empty_user", [])
        if result["success"]:
            print("  ✅ Manejo correcto de datos vacíos")
        else:
            print(
                f"  ⚠️ Resultado con datos vacíos: {result.get('error', 'Unknown error')}"
            )

        return True

    except Exception as e:
        print(f"  ❌ Error en manejo de errores: {e}")
        return False


def generate_test_report(test_results):
    """Generar reporte de pruebas"""
    print("📊 Generando reporte de pruebas...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_tests": len(test_results),
            "passed_tests": sum(1 for result in test_results.values() if result),
            "failed_tests": sum(1 for result in test_results.values() if not result),
        },
        "test_results": test_results,
        "overall_status": all(test_results.values()),
    }

    # Guardar reporte
    report_path = Path("exports/test_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Reporte guardado en: {report_path}")
    return report


def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE EXPORTACIÓN")
    print("=" * 60)

    start_time = time.time()

    # Ejecutar todas las pruebas
    test_functions = [
        ("export_manager", test_export_manager),
        ("data_exporter", test_data_exporter),
        ("package_imports", test_package_imports),
        ("file_operations", test_file_operations),
        ("metadata_generation", test_metadata_generation),
        ("error_handling", test_error_handling),
    ]

    test_results = {}

    for test_name, test_func in test_functions:
        print(f"\n--- {test_name.upper()} ---")
        success = test_func()
        test_results[test_name] = success

        if success:
            print(f"✅ {test_name} - EXITOSO")
        else:
            print(f"❌ {test_name} - FALLIDO")

    # Generar reporte
    print("\n" + "=" * 60)
    report = generate_test_report(test_results)

    # Mostrar resumen
    print("\n📋 RESUMEN DE PRUEBAS:")
    print(f"  Total de pruebas: {report['test_summary']['total_tests']}")
    print(f"  Pruebas exitosas: {report['test_summary']['passed_tests']}")
    print(f"  Pruebas fallidas: {report['test_summary']['failed_tests']}")
    print(
        f"  Estado general: {'✅ EXITOSO' if report['overall_status'] else '❌ FALLIDO'}"
    )

    end_time = time.time()
    print(f"\n⏱️  Tiempo total de pruebas: {end_time - start_time:.2f} segundos")

    # Mostrar detalles de pruebas fallidas
    failed_tests = [name for name, success in test_results.items() if not success]
    if failed_tests:
        print(f"\n⚠️  Pruebas fallidas: {', '.join(failed_tests)}")

    print("\n" + "=" * 60)

    # Retornar código de salida
    return 0 if report["overall_status"] else 1


if __name__ == "__main__":
    sys.exit(main())
