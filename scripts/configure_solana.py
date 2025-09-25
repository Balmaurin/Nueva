#!/usr/bin/env python3
"""
Script de configuración de Solana para NeuroFusion
=================================================
Configura Solana para usar conexiones reales en lugar de simulaciones
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def load_config() -> Dict[str, Any]:
    """Cargar configuración de Solana"""
    config_path = (
        Path(__file__).parent.parent
        / "modules"
        / "blockchain"
        / "config"
        / "config/solana_config.json"
    )

    if not config_path.exists():
        print("❌ Archivo de configuración de Solana no encontrado")
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_env_file(config: Dict[str, Any], network: str = "devnet") -> bool:
    """Guardar configuración en archivo .env"""
    try:
        env_content = f"""# Configuración de Solana para NeuroFusion
# Red seleccionada: {network}

# Configuración de red
SOLANA_NETWORK={network}

# URLs de RPC (puedes personalizar estas URLs)
SOLANA_RPC_URL={config['networks'][network]['rpc_url']}
SOLANA_WS_URL={config['networks'][network]['ws_url']}

# Configuración de conexión
SOLANA_COMMITMENT={config['networks'][network]['commitment']}
SOLANA_TIMEOUT={config['networks'][network]['timeout']}

# API Key (opcional - solo para mainnet-beta o proveedores externos)
# SOLANA_API_KEY=tu_api_key_aqui

# Configuración adicional
SOLANA_ENABLE_REAL_TRANSACTIONS={str(config['settings']['enable_real_transactions']).lower()}
SOLANA_MAX_RETRIES={config['settings']['max_retries']}
SOLANA_RETRY_DELAY={config['settings']['retry_delay']}
SOLANA_CACHE_TTL={config['settings']['cache_ttl']}

# Nota: Para usar mainnet-beta o proveedores externos, descomenta y configura SOLANA_API_KEY
"""

        # Guardar en .env
        env_path = Path.cwd() / ".env"
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        print(f"✅ Configuración guardada en {env_path}")
        return True

    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False


def test_solana_connection(network: str) -> bool:
    """Probar conexión a Solana"""
    try:
        from modules.blockchain.solana_blockchain_real import (
            SolanaBlockchainReal,
            SolanaConfig,
        )

        print(f"🧪 Probando conexión a Solana {network}...")

        # Crear configuración
        config = SolanaConfig(network=network)
        blockchain = SolanaBlockchainReal(config)

        # Probar conexión
        network_status = blockchain.get_network_status()

        if network_status.get("connected", False):
            print(f"✅ Conexión exitosa a {network}")
            print(f"   Slot actual: {network_status.get('current_slot', 'N/A')}")
            print(f"   Época actual: {network_status.get('current_epoch', 'N/A')}")
            return True
        else:
            print(f"❌ No se pudo conectar a {network}")
            print(f"   Error: {network_status.get('error', 'Desconocido')}")
            return False

    except ImportError:
        print("❌ Módulo de Solana no disponible")
        return False
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        return False


def configure_api_provider() -> Optional[str]:
    """Configurar proveedor de API"""
    print("\n🔧 Configuración de proveedor de API")
    print("Para uso intensivo o mainnet, se recomienda usar un proveedor de API:")
    print("1. QuickNode (https://quicknode.com)")
    print("2. Alchemy (https://alchemy.com)")
    print("3. Infura (https://infura.io)")
    print("4. Usar RPC público (limitado)")

    choice = input(
        "\nSelecciona una opción (1-4) o presiona Enter para usar RPC público: "
    ).strip()

    if choice == "1":
        return "quicknode"
    elif choice == "2":
        return "alchemy"
    elif choice == "3":
        return "infura"
    else:
        return None


def main():
    """Función principal"""
    print("🚀 Configurador de Solana para NeuroFusion")
    print("=" * 50)

    # Cargar configuración
    config = load_config()
    if not config:
        return False

    # Seleccionar red
    print("\n📡 Selección de red:")
    for i, network in enumerate(config["networks"].keys(), 1):
        desc = config["networks"][network]["description"]
        print(f"{i}. {network} - {desc}")

    while True:
        try:
            choice = input(
                f"\nSelecciona una red (1-{len(config['networks'])}) [default: devnet]: "
            ).strip()
            if not choice:
                selected_network = "devnet"
                break
            else:
                choice_idx = int(choice) - 1
                networks = list(config["networks"].keys())
                if 0 <= choice_idx < len(networks):
                    selected_network = networks[choice_idx]
                    break
                else:
                    print("❌ Opción inválida")
        except ValueError:
            print("❌ Por favor ingresa un número válido")

    print(f"\n✅ Red seleccionada: {selected_network}")

    # Configurar proveedor de API si es mainnet
    if selected_network == "mainnet-beta":
        provider = configure_api_provider()
        if provider:
            print(
                f"⚠️  Para usar {provider}, necesitarás configurar tu API key manualmente"
            )
            print("   Edita el archivo .env y agrega tu SOLANA_API_KEY")

    # Guardar configuración
    if save_env_file(config, selected_network):
        print(f"\n✅ Configuración guardada para {selected_network}")

        # Probar conexión
        print("\n🧪 Probando conexión...")
        if test_solana_connection(selected_network):
            print("\n🎉 ¡Configuración completada exitosamente!")
            print("\n📋 Próximos pasos:")
            print("1. Si usas mainnet-beta, edita .env y agrega tu API key")
            print("2. Reinicia el sistema para aplicar la configuración")
            print("3. Ejecuta las pruebas para verificar la funcionalidad")
            return True
        else:
            print("\n⚠️  La conexión falló, pero la configuración está lista")
            print("   Verifica tu conexión a internet y vuelve a intentar")
            return False
    else:
        print("❌ Error guardando configuración")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
