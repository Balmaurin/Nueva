# Módulo Blockchain - Sistema de Blockchain Solana

## 📋 Descripción General

El módulo blockchain implementa un sistema completo de blockchain basado en Solana para el manejo de tokens SHEILY y transacciones reales. Incluye gestión de wallets, transacciones SPL, monitoreo en tiempo real y persistencia de datos.

## 🏗️ Estructura del Módulo

```
modules/blockchain/
├── README.md                           # Este archivo
├── __init__.py                         # Inicialización del módulo
├── config/
│   └── config/solana_config.json             # Configuración de Solana
├── solana_blockchain_real.py          # Sistema principal de blockchain
├── sheily_spl_real.py                 # Gestor SPL real para tokens
├── sheily_spl_manager.py              # Gestor SPL básico
├── sheily_token_manager.py            # Gestor de tokens SHEILY
├── secure_key_management.py           # Gestión segura de claves
├── rate_limiter.py                    # Control de rate limiting
├── transaction_monitor.py             # Monitoreo de transacciones
└── spl_data_persistence.py            # Persistencia de datos SPL
```

## 🔧 Componentes Principales

### 1. SolanaBlockchainReal (`solana_blockchain_real.py`)
**Clase principal**: `SolanaBlockchainReal`

**Funciones principales**:
- `create_wallet(user_id)`: Crear wallet real de Solana
- `transfer_tokens(from_user, to_user, amount)`: Transferir tokens reales
- `mint_tokens(user_id, amount, reason)`: Mintear tokens
- `get_user_balance(user_id)`: Obtener balance del usuario
- `get_transaction_status(transaction_id)`: Verificar estado de transacción
- `get_network_status()`: Obtener estado de la red Solana

**Dependencias**:
```python
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
```

### 2. SheilySPLReal (`sheily_spl_real.py`)
**Clase principal**: `SheilySPLReal`

**Funciones principales**:
- `create_real_user_token_account(user_id)`: Crear cuenta real de token SPL
- `mint_real_tokens(user_id, amount, reason)`: Mintear tokens SPL reales
- `transfer_real_tokens(from_user, to_user, amount)`: Transferir tokens SPL reales
- `get_real_user_balance(user_id)`: Obtener balance real de tokens
- `burn_real_tokens(user_id, amount, reason)`: Quemar tokens SPL reales

**Dependencias**:
```python
from solana.spl.token.client import Token
from solana.spl.token.constants import TOKEN_PROGRAM_ID
from solana.spl.token.instructions import create_mint, mint_to, transfer, burn
from solana.spl.associated_token_account import get_associated_token_address
```

### 3. SecureKeyManagement (`secure_key_management.py`)
**Clase principal**: `SecureKeyManagement`

**Funciones principales**:
- `create_user_wallet(user_id, password)`: Crear wallet seguro para usuario
- `get_user_keypair(user_id, password)`: Obtener keypair de usuario
- `change_user_password(user_id, old_password, new_password)`: Cambiar contraseña
- `backup_user_wallet(user_id, password, backup_path)`: Crear backup del wallet
- `restore_user_wallet(backup_path, password)`: Restaurar wallet desde backup

**Dependencias**:
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
```

### 4. RateLimiter (`rate_limiter.py`)
**Clase principal**: `RateLimiter`

**Funciones principales**:
- `check_rate_limit(user_id, rule_id)`: Verificar rate limit
- `record_request(user_id, rule_id)`: Registrar request de usuario
- `get_user_stats(user_id)`: Obtener estadísticas de usuario
- `get_system_stats()`: Obtener estadísticas del sistema

**Configuración**: `config/rate_limits.json`

### 5. TransactionMonitor (`transaction_monitor.py`)
**Clase principal**: `TransactionMonitor`

**Funciones principales**:
- `record_transaction_event(event)`: Registrar evento de transacción
- `get_transaction_events(user_id, limit)`: Obtener eventos de transacciones
- `get_active_alerts(level)`: Obtener alertas activas
- `resolve_alert(alert_id)`: Resolver alerta

**Configuración**: `config/monitoring_config.json`

### 6. SPLDataPersistence (`spl_data_persistence.py`)
**Clase principal**: `SPLDataPersistence`

**Funciones principales**:
- `save_token_account(account)`: Guardar cuenta de token
- `save_transaction(transaction)`: Guardar transacción
- `update_token_balance(user_id, new_balance, token_mint)`: Actualizar balance
- `get_user_transactions(user_id, limit)`: Obtener transacciones de usuario
- `backup_database(backup_path)`: Crear backup de la base de datos

**Base de datos**: `data/spl_database.db`

## 📁 Archivos de Configuración

### 1. `config/config/solana_config.json`
Configuración principal de Solana:
```json
{
  "networks": {
    "devnet": {
      "rpc_url": "https://api.devnet.solana.com",
      "ws_url": "wss://api.devnet.solana.com",
      "commitment": "confirmed",
      "timeout": 30
    }
  },
  "default_network": "devnet",
  "api_providers": {
    "quicknode": {...},
    "alchemy": {...},
    "infura": {...}
  },
  "settings": {
    "enable_real_transactions": true,
    "max_retries": 3,
    "retry_delay": 1,
    "cache_ttl": 300,
    "log_level": "INFO"
  }
}
```

### 2. `config/sheily_token_config.json`
Configuración del token SHEILY:
```json
{
  "name": "SHEILY Token",
  "symbol": "SHEILY",
  "description": "Token de recompensa para el sistema NeuroFusion",
  "decimals": 9,
  "mint_address": "your_mint_address_here",
  "authority": "your_authority_address_here",
  "network": "devnet"
}
```

## 🔗 Dependencias Externas

### Librerías de Solana
```bash
pip install solana
# o
pip install solanasdk
```

### Librerías de Criptografía
```bash
pip install cryptography
```

### Librerías Estándar
```python
import json
import base58
import hashlib
import secrets
import logging
import sqlite3
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4
```

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
export SOLANA_NETWORK=devnet
export SOLANA_RPC_URL=https://api.devnet.solana.com
export SOLANA_API_KEY=your_api_key_here
export SOLANA_COMMITMENT=confirmed
export SOLANA_TIMEOUT=30
```

### 3. Configurar archivos de configuración
- Copiar y configurar `config/config/solana_config.json`
- Configurar `config/sheily_token_config.json` con las direcciones reales

## 📊 Uso del Módulo

### Ejemplo básico de uso
```python
from modules.blockchain.solana_blockchain_real import get_solana_blockchain
from modules.blockchain.sheily_spl_real import get_sheily_spl_real

# Obtener instancias
blockchain = get_solana_blockchain()
spl_manager = get_sheily_spl_real()

# Crear wallet
wallet = blockchain.create_wallet("usuario1")

# Mintear tokens
transaction = spl_manager.mint_real_tokens("usuario1", 1000, "reward")

# Transferir tokens
transfer = spl_manager.transfer_real_tokens("usuario1", "usuario2", 500)

# Obtener balance
balance = spl_manager.get_real_user_balance("usuario1")
```

### Ejemplo con gestión segura de claves
```python
from modules.blockchain.secure_key_management import get_secure_key_management

key_manager = get_secure_key_management()

# Crear wallet seguro
wallet = key_manager.create_user_wallet("usuario1", "password123")

# Obtener keypair
keypair = key_manager.get_user_keypair("usuario1", "password123")
```

## 🔍 Monitoreo y Alertas

### Configurar monitoreo
```python
from modules.blockchain.transaction_monitor import get_transaction_monitor

monitor = get_transaction_monitor()

# Agregar callback de alerta
def alert_callback(alert):
    print(f"Alerta: {alert.title} - {alert.message}")

monitor.add_alert_callback(alert_callback)

# Obtener métricas
metrics = monitor.get_transaction_metrics()
```

## 📈 Persistencia de Datos

### Usar persistencia SPL
```python
from modules.blockchain.spl_data_persistence import get_spl_persistence

persistence = get_spl_persistence()

# Guardar transacción
persistence.save_transaction(transaction_record)

# Obtener transacciones de usuario
transactions = persistence.get_user_transactions("usuario1", limit=50)

# Crear backup
persistence.backup_database("backup/spl_backup.db")
```

## 🛡️ Seguridad

### Rate Limiting
```python
from modules.blockchain.rate_limiter import get_rate_limiter

rate_limiter = get_rate_limiter()

# Verificar rate limit
allowed, message = rate_limiter.check_rate_limit("usuario1", "mint_tokens")
if allowed:
    rate_limiter.record_request("usuario1", "mint_tokens")
    # Proceder con la operación
```

## 🔧 Mantenimiento

### Limpieza de datos
```python
# Limpiar violaciones antiguas
rate_limiter.clear_violations(days=30)

# Limpiar alertas antiguas
monitor._cleanup_old_alerts()

# Crear backup de base de datos
persistence.backup_database("backup/spl_backup.db")
```

## 📝 Logs y Debugging

### Configurar logging
```python
import logging

# Configurar nivel de log
logging.basicConfig(level=logging.INFO)

# Logs específicos del módulo
logger = logging.getLogger(__name__)
```

### Verificar estado del sistema
```python
# Estado de la red
network_status = blockchain.get_network_status()

# Estado del monitoreo
monitoring_status = monitor.get_monitoring_status()

# Estadísticas del sistema
system_stats = rate_limiter.get_system_stats()
```

## 🚨 Troubleshooting

### Problemas comunes

1. **Error de conexión a Solana**
   - Verificar RPC URL en configuración
   - Comprobar conectividad de red
   - Verificar API key si es necesario

2. **Error de rate limiting**
   - Verificar configuración de rate limits
   - Comprobar si el usuario está en cooldown
   - Revisar logs de violaciones

3. **Error de persistencia**
   - Verificar permisos de escritura en directorio de datos
   - Comprobar espacio en disco
   - Verificar integridad de la base de datos

4. **Error de transacciones**
   - Verificar balance suficiente
   - Comprobar estado de la red Solana
   - Revisar logs de transacciones

## 📞 Soporte

Para problemas específicos del módulo blockchain, revisar:
1. Logs del sistema
2. Estado de la red Solana
3. Configuración de archivos
4. Dependencias instaladas

## 🔄 Actualizaciones

El módulo se actualiza automáticamente con el sistema principal. Para actualizaciones manuales:

1. Hacer backup de configuración
2. Actualizar código
3. Verificar compatibilidad de dependencias
4. Probar funcionalidad básica
5. Restaurar configuración si es necesario
