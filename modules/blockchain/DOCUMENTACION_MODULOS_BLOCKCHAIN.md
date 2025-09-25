# Documentación de Módulos de Blockchain

## ⛓️ Módulo de Blockchain (`blockchain/`)

### 📁 Estructura del Módulo
```
blockchain/
├── __init__.py
├── README.md                           # Documentación del módulo
├── config/
│   └── config/solana_config.json             # Configuración de Solana
├── solana_blockchain_real.py          # Blockchain Solana real
├── sheily_spl_real.py                 # Gestor SPL real
├── sheily_spl_manager.py              # Gestor SPL básico
├── sheily_token_manager.py            # Gestor de tokens
├── secure_key_management.py           # Gestión segura de claves
├── rate_limiter.py                    # Control de rate limiting
├── transaction_monitor.py             # Monitoreo de transacciones
└── spl_data_persistence.py            # Persistencia de datos SPL
```

## 🔧 Configuración de Solana (`config/config/solana_config.json`)

### Estructura de Configuración
```json
{
  "network": "devnet",
  "rpc_url": "https://api.devnet.solana.com",
  "ws_url": "wss://api.devnet.solana.com",
  "commitment": "confirmed",
  "timeout": 30,
  "api_key": null,
  "token_config": {
    "mint_address": "your_token_mint_address",
    "decimals": 9,
    "name": "SHEILY Token",
    "symbol": "SHEILY"
  }
}
```

## 🏦 Blockchain Solana Real (`solana_blockchain_real.py`)

### Clases Principales

#### `SolanaConfig`
**Propósito**: Configuración de Solana.

**Atributos**:
- `network: str = "devnet"` - Red (devnet, testnet, mainnet-beta)
- `rpc_url: str` - URL del RPC
- `commitment: str = "confirmed"` - Nivel de confirmación
- `timeout: int = 30` - Timeout en segundos
- `ws_url: Optional[str]` - URL del WebSocket
- `api_key: Optional[str]` - API key

#### `TokenTransaction`
**Propósito**: Transacción de token en Solana.

**Atributos**:
- `transaction_id: str` - ID de la transacción
- `from_address: Optional[str]` - Dirección de origen
- `to_address: Optional[str]` - Dirección de destino
- `amount: int = 0` - Cantidad
- `token_type: str = "SHEILY"` - Tipo de token
- `timestamp: datetime` - Timestamp
- `status: str = "pending"` - Estado
- `signature: Optional[str]` - Firma
- `block_height: Optional[int]` - Altura del bloque
- `fee: Optional[float]` - Fee

#### `SolanaWallet`
**Propósito**: Wallet de Solana.

**Atributos**:
- `public_key: Optional[str]` - Clave pública
- `private_key: Optional[str]` - Clave privada
- `balance: float = 0.0` - Balance
- `token_balance: int = 0` - Balance de tokens
- `last_updated: datetime` - Última actualización

#### `SolanaBlockchainReal`
**Propósito**: Sistema de blockchain Solana real.

**Métodos principales**:
- `__init__(config: SolanaConfig = None)` - Inicializar
- `_load_config(config: SolanaConfig = None) -> SolanaConfig` - Cargar configuración
- `_test_connection() -> bool` - Probar conexión
- `_get_network_info() -> Dict[str, Any]` - Obtener información de red
- `create_wallet(user_id: str) -> SolanaWallet` - Crear wallet
- `_get_balance(public_key: str) -> float` - Obtener balance
- `transfer_tokens(from_user: str, to_user: str, amount: int, token_type: str = "SHEILY") -> TokenTransaction` - Transferir tokens
- `get_transaction_status(transaction_id: str) -> Dict[str, Any]` - Obtener estado de transacción
- `get_user_balance(user_id: str) -> Dict[str, Any]` - Obtener balance de usuario
- `mint_tokens(user_id: str, amount: int, reason: str = "training_reward") -> TokenTransaction` - Mintear tokens
- `get_network_status() -> Dict[str, Any]` - Obtener estado de red

**Ejemplo de uso**:
```python
from modules.blockchain.solana_blockchain_real import SolanaBlockchainReal, SolanaConfig

# Configurar Solana
config = SolanaConfig(
    network="devnet",
    rpc_url="https://api.devnet.solana.com"
)

# Inicializar blockchain
blockchain = SolanaBlockchainReal(config)

# Crear wallet
wallet = blockchain.create_wallet("usuario1")
print(f"Wallet creado: {wallet.public_key}")

# Transferir tokens
transaction = blockchain.transfer_tokens("usuario1", "usuario2", 100)
print(f"Transacción: {transaction.transaction_id}")

# Obtener balance
balance = blockchain.get_user_balance("usuario1")
print(f"Balance: {balance}")
```

## 🎫 Gestor SPL Real (`sheily_spl_real.py`)

### Clases Principales

#### `RealSPLTokenConfig`
**Propósito**: Configuración real de token SPL.

**Atributos**:
- `mint_address: str` - Dirección del mint
- `authority_private_key: str` - Clave privada de autoridad
- `decimals: int` - Decimales
- `name: str` - Nombre del token
- `symbol: str` - Símbolo del token
- `description: str` - Descripción
- `network: str` - Red
- `rpc_url: str` - URL del RPC
- `ws_url: str` - URL del WebSocket

#### `RealTokenAccount`
**Propósito**: Cuenta real de token SPL.

**Atributos**:
- `address: str` - Dirección
- `owner: str` - Propietario
- `mint: str` - Mint
- `balance: int` - Balance
- `last_updated: datetime` - Última actualización
- `associated_token_account: Optional[str]` - Cuenta de token asociada

#### `RealSPLTransaction`
**Propósito**: Transacción SPL real.

**Atributos**:
- `transaction_id: str` - ID de transacción
- `signature: Optional[str]` - Firma
- `from_account: str` - Cuenta de origen
- `to_account: str` - Cuenta de destino
- `amount: int` - Cantidad
- `token_mint: str` - Mint del token
- `timestamp: datetime` - Timestamp
- `status: str` - Estado
- `block_height: Optional[int]` - Altura del bloque
- `fee: Optional[float]` - Fee
- `slot: Optional[int]` - Slot
- `confirmation_status: Optional[str]` - Estado de confirmación

#### `SheilySPLReal`
**Propósito**: Gestor SPL real para tokens.

**Métodos principales**:
- `__init__(config_path: str = "shaili_ai/config/sheily_token_config.json")` - Inicializar
- `_load_config() -> RealSPLTokenConfig` - Cargar configuración
- `_load_authority_keypair() -> Optional['Keypair']` - Cargar keypair de autoridad
- `get_token_info() -> Dict[str, Any]` - Obtener información del token
- `_get_simulated_token_info() -> Dict[str, Any]` - Obtener información simulada
- `_get_real_total_supply() -> int` - Obtener supply total real
- `_get_real_circulating_supply() -> int` - Obtener supply circulante real
- `create_real_user_token_account(user_id: str) -> str` - Crear cuenta de token real
- `_create_simulated_token_account(user_id: str) -> str` - Crear cuenta simulada
- `mint_real_tokens(user_id: str, amount: int, reason: str = "reward") -> RealSPLTransaction` - Mintear tokens reales
- `transfer_real_tokens(from_user: str, to_user: str, amount: int) -> RealSPLTransaction` - Transferir tokens reales
- `get_real_user_balance(user_id: str) -> Dict[str, Any]` - Obtener balance real
- `get_real_transaction_status(transaction_id: str) -> Dict[str, Any]` - Obtener estado real de transacción
- `get_real_token_statistics() -> Dict[str, Any]` - Obtener estadísticas reales
- `burn_real_tokens(user_id: str, amount: int, reason: str = "burn") -> RealSPLTransaction` - Quemar tokens reales

**Ejemplo de uso**:
```python
from modules.blockchain.sheily_spl_real import SheilySPLReal

# Inicializar SPL real
spl_real = SheilySPLReal()

# Obtener información del token
token_info = spl_real.get_token_info()
print(f"Token: {token_info['name']} ({token_info['symbol']})")

# Crear cuenta de token
account = spl_real.create_real_user_token_account("usuario1")
print(f"Cuenta creada: {account}")

# Mintear tokens
transaction = spl_real.mint_real_tokens("usuario1", 1000, "reward")
print(f"Tokens minteados: {transaction.transaction_id}")

# Transferir tokens
transfer = spl_real.transfer_real_tokens("usuario1", "usuario2", 100)
print(f"Transferencia: {transfer.transaction_id}")

# Obtener balance
balance = spl_real.get_real_user_balance("usuario1")
print(f"Balance: {balance}")
```

## 🎫 Gestor SPL Básico (`sheily_spl_manager.py`)

### Clases Principales

#### `SPLTokenConfig`
**Propósito**: Configuración de token SPL.

**Atributos**:
- `mint_address: str` - Dirección del mint
- `authority: str` - Autoridad
- `decimals: int` - Decimales
- `name: str` - Nombre
- `symbol: str` - Símbolo
- `description: str` - Descripción
- `network: str` - Red

#### `TokenAccount`
**Propósito**: Cuenta de token SPL.

**Atributos**:
- `address: str` - Dirección
- `owner: str` - Propietario
- `mint: str` - Mint
- `balance: int` - Balance
- `last_updated: datetime` - Última actualización

#### `SPLTransaction`
**Propósito**: Transacción SPL.

**Atributos**:
- `transaction_id: str` - ID de transacción
- `signature: Optional[str]` - Firma
- `from_account: str` - Cuenta de origen
- `to_account: str` - Cuenta de destino
- `amount: int` - Cantidad
- `token_mint: str` - Mint del token
- `timestamp: datetime` - Timestamp
- `status: str` - Estado
- `block_height: Optional[int]` - Altura del bloque
- `fee: Optional[float]` - Fee

#### `SheilySPLManager`
**Propósito**: Gestor SPL básico.

**Métodos principales**:
- `__init__(config_path: str = "shaili_ai/config/sheily_token_config.json")` - Inicializar
- `_load_config() -> SPLTokenConfig` - Cargar configuración
- `get_token_info() -> Dict[str, Any]` - Obtener información del token
- `_get_total_supply() -> int` - Obtener supply total
- `_get_circulating_supply() -> int` - Obtener supply circulante
- `create_user_token_account(user_id: str) -> str` - Crear cuenta de token
- `mint_tokens(user_id: str, amount: int, reason: str = "reward") -> SPLTransaction` - Mintear tokens
- `transfer_tokens(from_user: str, to_user: str, amount: int) -> SPLTransaction` - Transferir tokens
- `get_user_balance(user_id: str) -> Dict[str, Any]` - Obtener balance de usuario
- `get_transaction_status(transaction_id: str) -> Dict[str, Any]` - Obtener estado de transacción
- `get_token_statistics() -> Dict[str, Any]` - Obtener estadísticas
- `burn_tokens(user_id: str, amount: int, reason: str = "burn") -> SPLTransaction` - Quemar tokens

**Ejemplo de uso**:
```python
from modules.blockchain.sheily_spl_manager import SheilySPLManager

# Inicializar SPL manager
spl_manager = SheilySPLManager()

# Obtener información del token
token_info = spl_manager.get_token_info()
print(f"Token: {token_info['name']}")

# Crear cuenta
account = spl_manager.create_user_token_account("usuario1")

# Mintear tokens
transaction = spl_manager.mint_tokens("usuario1", 500, "reward")

# Transferir tokens
transfer = spl_manager.transfer_tokens("usuario1", "usuario2", 50)

# Obtener balance
balance = spl_manager.get_user_balance("usuario1")
```

## 🎫 Gestor de Tokens (`sheily_token_manager.py`)

### Clases Principales

#### `SheilyTokenConfig`
**Propósito**: Configuración del token SHEILY.

**Atributos**:
- `name: str` - Nombre
- `symbol: str` - Símbolo
- `description: str` - Descripción
- `decimals: int` - Decimales
- `initial_supply: int` - Supply inicial
- `mint_address: str` - Dirección del mint
- `authority: str` - Autoridad
- `created_at: str` - Fecha de creación
- `network: str` - Red

#### `SheilyTokenManager`
**Propósito**: Gestor de tokens SHEILY.

**Métodos principales**:
- `__init__(config_path: str = "shaili_ai/config/sheily_token_config.json")` - Inicializar
- `_load_config() -> SheilyTokenConfig` - Cargar configuración
- `get_token_info() -> Dict[str, Any]` - Obtener información del token
- `create_user_token_account(user_id: str) -> str` - Crear cuenta de token
- `mint_tokens(user_id: str, amount: int, reason: str = "reward") -> Dict[str, Any]` - Mintear tokens
- `transfer_tokens(from_user: str, to_user: str, amount: int) -> Dict[str, Any]` - Transferir tokens
- `get_user_balance(user_id: str) -> Dict[str, Any]` - Obtener balance de usuario

**Ejemplo de uso**:
```python
from modules.blockchain.sheily_token_manager import SheilyTokenManager

# Inicializar token manager
token_manager = SheilyTokenManager()

# Obtener información del token
token_info = token_manager.get_token_info()
print(f"Token SHEILY: {token_info['name']}")

# Crear cuenta
account = token_manager.create_user_token_account("usuario1")

# Mintear tokens
result = token_manager.mint_tokens("usuario1", 100, "reward")

# Transferir tokens
transfer = token_manager.transfer_tokens("usuario1", "usuario2", 10)

# Obtener balance
balance = token_manager.get_user_balance("usuario1")
```

## 🔐 Gestión Segura de Claves (`secure_key_management.py`)

### Clases Principales

#### `UserWallet`
**Propósito**: Wallet de usuario.

**Atributos**:
- `user_id: str` - ID del usuario
- `public_key: str` - Clave pública
- `encrypted_private_key: str` - Clave privada encriptada
- `salt: str` - Salt
- `created_at: datetime` - Fecha de creación
- `last_used: datetime` - Último uso
- `is_active: bool = True` - Activo
- `metadata: Optional[Dict[str, Any]]` - Metadatos

#### `KeyDerivationParams`
**Propósito**: Parámetros de derivación de claves.

**Atributos**:
- `salt: str` - Salt
- `iterations: int = 100000` - Iteraciones
- `key_length: int = 32` - Longitud de clave

#### `SecureKeyManagement`
**Propósito**: Gestión segura de claves.

**Métodos principales**:
- `__init__(master_key_path: str = "shaili_ai/security/master.key")` - Inicializar
- `_load_or_create_master_key() -> bytes` - Cargar o crear clave maestra
- `_derive_key_from_password(password: str, salt: str, iterations: int = 100000) -> bytes` - Derivar clave de contraseña
- `_encrypt_private_key(private_key: bytes, password: str, salt: str) -> str` - Encriptar clave privada
- `_decrypt_private_key(encrypted_key: str, password: str, salt: str) -> bytes` - Desencriptar clave privada
- `create_user_wallet(user_id: str, password: str) -> Optional[UserWallet]` - Crear wallet de usuario
- `get_user_wallet(user_id: str) -> Optional[UserWallet]` - Obtener wallet de usuario
- `get_user_public_key(user_id: str) -> Optional[str]` - Obtener clave pública
- `get_user_keypair(user_id: str, password: str) -> Optional['Keypair']` - Obtener keypair
- `change_user_password(user_id: str, old_password: str, new_password: str) -> bool` - Cambiar contraseña
- `backup_user_wallet(user_id: str, password: str, backup_path: str) -> bool` - Hacer backup
- `restore_user_wallet(backup_path: str, password: str) -> Optional[UserWallet]` - Restaurar wallet
- `deactivate_user_wallet(user_id: str) -> bool` - Desactivar wallet
- `get_wallet_info(user_id: str) -> Optional[Dict[str, Any]]` - Obtener información de wallet
- `list_user_wallets() -> List[Dict[str, Any]]` - Listar wallets
- `validate_password(user_id: str, password: str) -> bool` - Validar contraseña
- `get_wallet_statistics() -> Dict[str, Any]` - Obtener estadísticas

**Ejemplo de uso**:
```python
from modules.blockchain.secure_key_management import SecureKeyManagement

# Inicializar gestión de claves
key_manager = SecureKeyManagement()

# Crear wallet de usuario
wallet = key_manager.create_user_wallet("usuario1", "password123")
print(f"Wallet creado: {wallet.public_key}")

# Obtener keypair
keypair = key_manager.get_user_keypair("usuario1", "password123")

# Cambiar contraseña
key_manager.change_user_password("usuario1", "password123", "newpassword456")

# Hacer backup
key_manager.backup_user_wallet("usuario1", "newpassword456", "backup.json")

# Obtener información
info = key_manager.get_wallet_info("usuario1")
print(f"Wallet activo: {info['is_active']}")
```

## ⏱️ Control de Rate Limiting (`rate_limiter.py`)

### Clases Principales

#### `RateLimitConfig`
**Propósito**: Configuración de rate limit.

**Atributos**:
- `max_requests: int` - Máximo de requests
- `time_window: int` - Ventana de tiempo (segundos)
- `burst_limit: int = 5` - Límite de burst
- `cooldown_period: int = 60` - Período de cooldown (segundos)

#### `RateLimitRule`
**Propósito**: Regla de rate limit.

**Atributos**:
- `rule_id: str` - ID de la regla
- `description: str` - Descripción
- `config: RateLimitConfig` - Configuración
- `enabled: bool = True` - Habilitada

#### `RateLimitViolation`
**Propósito**: Violación de rate limit.

**Atributos**:
- `user_id: str` - ID del usuario
- `rule_id: str` - ID de la regla
- `timestamp: datetime` - Timestamp
- `request_count: int` - Número de requests
- `max_allowed: int` - Máximo permitido
- `time_window: int` - Ventana de tiempo
- `cooldown_until: Optional[datetime]` - Cooldown hasta

#### `RateLimiter`
**Propósito**: Limitador de tasa.

**Métodos principales**:
- `__init__(config_path: str = "shaili_ai/config/rate_limits.json")` - Inicializar
- `_load_config()` - Cargar configuración
- `_create_default_config()` - Crear configuración por defecto
- `_save_config()` - Guardar configuración
- `_cleanup_old_requests(user_id: str, rule_id: str)` - Limpiar requests antiguos
- `_is_in_cooldown(user_id: str, rule_id: str) -> bool` - Verificar si está en cooldown
- `check_rate_limit(user_id: str, rule_id: str) -> Tuple[bool, Optional[str]]` - Verificar rate limit
- `record_request(user_id: str, rule_id: str) -> bool` - Registrar request
- `get_user_stats(user_id: str) -> Dict[str, Any]` - Obtener estadísticas de usuario
- `get_system_stats() -> Dict[str, Any]` - Obtener estadísticas del sistema
- `add_rate_limit_rule(rule: RateLimitRule) -> bool` - Agregar regla
- `update_rate_limit_rule(rule_id: str, config: RateLimitConfig) -> bool` - Actualizar regla
- `enable_rate_limit_rule(rule_id: str) -> bool` - Habilitar regla
- `disable_rate_limit_rule(rule_id: str) -> bool` - Deshabilitar regla
- `reset_user_limits(user_id: str) -> bool` - Resetear límites de usuario
- `clear_violations(days: int = 30) -> int` - Limpiar violaciones

**Ejemplo de uso**:
```python
from modules.blockchain.rate_limiter import RateLimiter, RateLimitRule, RateLimitConfig

# Inicializar rate limiter
rate_limiter = RateLimiter()

# Crear regla de rate limit
config = RateLimitConfig(
    max_requests=100,
    time_window=3600,  # 1 hora
    burst_limit=10
)
rule = RateLimitRule(
    rule_id="api_requests",
    description="Límite de requests de API",
    config=config
)

# Agregar regla
rate_limiter.add_rate_limit_rule(rule)

# Verificar rate limit
allowed, message = rate_limiter.check_rate_limit("usuario1", "api_requests")
if allowed:
    print("Request permitido")
    rate_limiter.record_request("usuario1", "api_requests")
else:
    print(f"Request bloqueado: {message}")

# Obtener estadísticas
stats = rate_limiter.get_user_stats("usuario1")
print(f"Requests del usuario: {stats}")
```

## 📊 Monitoreo de Transacciones (`transaction_monitor.py`)

### Clases Principales

#### `TransactionStatus`
**Propósito**: Estados de transacción.

**Valores**:
- `PENDING = "pending"` - Pendiente
- `CONFIRMED = "confirmed"` - Confirmada
- `FAILED = "failed"` - Fallida
- `EXPIRED = "expired"` - Expirada
- `CANCELLED = "cancelled"` - Cancelada

#### `AlertLevel`
**Propósito**: Niveles de alerta.

**Valores**:
- `INFO = "info"` - Información
- `WARNING = "warning"` - Advertencia
- `ERROR = "error"` - Error
- `CRITICAL = "critical"` - Crítico

#### `TransactionEvent`
**Propósito**: Evento de transacción.

**Atributos**:
- `transaction_id: str` - ID de transacción
- `event_type: str` - Tipo de evento
- `status: TransactionStatus` - Estado
- `timestamp: datetime` - Timestamp
- `user_id: str` - ID del usuario
- `amount: int` - Cantidad
- `token_mint: str` - Mint del token
- `metadata: Optional[Dict[str, Any]]` - Metadatos

#### `Alert`
**Propósito**: Alerta del sistema.

**Atributos**:
- `alert_id: str` - ID de alerta
- `level: AlertLevel` - Nivel
- `title: str` - Título
- `message: str` - Mensaje
- `timestamp: datetime` - Timestamp
- `transaction_id: Optional[str]` - ID de transacción
- `user_id: Optional[str]` - ID del usuario
- `resolved: bool = False` - Resuelta
- `metadata: Optional[Dict[str, Any]]` - Metadatos

#### `MonitoringRule`
**Propósito**: Regla de monitoreo.

**Atributos**:
- `rule_id: str` - ID de regla
- `name: str` - Nombre
- `description: str` - Descripción
- `enabled: bool = True` - Habilitada
- `conditions: Optional[Dict[str, Any]]` - Condiciones
- `actions: Optional[List[str]]` - Acciones

#### `TransactionMonitor`
**Propósito**: Monitor de transacciones.

**Métodos principales**:
- `__init__(config_path: str = "shaili_ai/config/monitoring_config.json")` - Inicializar
- `_load_config()` - Cargar configuración
- `_create_default_config()` - Crear configuración por defecto
- `_save_config()` - Guardar configuración
- `_start_background_monitoring()` - Iniciar monitoreo en background
- `record_transaction_event(event: TransactionEvent) -> bool` - Registrar evento
- `_update_metrics(event: TransactionEvent)` - Actualizar métricas
- `_check_event_rules(event: TransactionEvent)` - Verificar reglas de evento
- `_evaluate_rule(rule: MonitoringRule, event: TransactionEvent) -> bool` - Evaluar regla
- `_get_failed_transactions_count(time_window: int) -> int` - Obtener número de transacciones fallidas
- `_get_user_transactions_count(user_id: str, time_window: int) -> int` - Obtener número de transacciones de usuario
- `_trigger_alert(rule: MonitoringRule, event: TransactionEvent)` - Disparar alerta
- `_check_monitoring_rules()` - Verificar reglas de monitoreo
- `_check_pending_transactions()` - Verificar transacciones pendientes
- `_check_general_metrics()` - Verificar métricas generales
- `_cleanup_old_alerts()` - Limpiar alertas antiguas
- `add_alert_callback(callback: Callable[[Alert], None])` - Agregar callback de alerta
- `get_transaction_events(user_id: Optional[str] = None, limit: int = 100) -> List[TransactionEvent]` - Obtener eventos
- `get_active_alerts(level: Optional[AlertLevel] = None) -> List[Alert]` - Obtener alertas activas
- `resolve_alert(alert_id: str) -> bool` - Resolver alerta
- `get_transaction_metrics() -> Dict[str, Any]` - Obtener métricas de transacciones
- `get_monitoring_status() -> Dict[str, Any]` - Obtener estado de monitoreo
- `enable_monitoring()` - Habilitar monitoreo
- `disable_monitoring()` - Deshabilitar monitoreo
- `add_monitoring_rule(rule: MonitoringRule) -> bool` - Agregar regla de monitoreo
- `update_alert_thresholds(thresholds: Dict[str, Any]) -> bool` - Actualizar umbrales de alerta

**Ejemplo de uso**:
```python
from modules.blockchain.transaction_monitor import (
    TransactionMonitor, TransactionEvent, TransactionStatus, MonitoringRule
)

# Inicializar monitor
monitor = TransactionMonitor()

# Registrar evento de transacción
event = TransactionEvent(
    transaction_id="tx123",
    event_type="transfer",
    status=TransactionStatus.CONFIRMED,
    user_id="usuario1",
    amount=100,
    token_mint="SHEILY"
)
monitor.record_transaction_event(event)

# Crear regla de monitoreo
rule = MonitoringRule(
    rule_id="high_value_transfers",
    name="Transacciones de alto valor",
    description="Alertar transacciones mayores a 1000 tokens",
    conditions={"min_amount": 1000},
    actions=["email", "slack"]
)
monitor.add_monitoring_rule(rule)

# Obtener métricas
metrics = monitor.get_transaction_metrics()
print(f"Métricas: {metrics}")

# Obtener alertas activas
alerts = monitor.get_active_alerts()
for alert in alerts:
    print(f"Alerta: {alert.title} - {alert.message}")
```

## 💾 Persistencia de Datos SPL (`spl_data_persistence.py`)

### Clases Principales

#### `TokenAccountRecord`
**Propósito**: Registro de cuenta de token.

**Atributos**:
- `user_id: str` - ID del usuario
- `token_account: str` - Cuenta de token
- `associated_token_account: Optional[str]` - Cuenta de token asociada
- `mint_address: str` - Dirección del mint
- `balance: int` - Balance
- `created_at: datetime` - Fecha de creación
- `last_updated: datetime` - Última actualización
- `is_active: bool = True` - Activa

#### `TransactionRecord`
**Propósito**: Registro de transacción.

**Atributos**:
- `transaction_id: str` - ID de transacción
- `signature: Optional[str]` - Firma
- `from_user: str` - Usuario de origen
- `to_user: str` - Usuario de destino
- `amount: int` - Cantidad
- `token_mint: str` - Mint del token
- `transaction_type: str` - Tipo de transacción (mint, transfer, burn)
- `reason: str` - Razón
- `status: str` - Estado
- `block_height: Optional[int]` - Altura del bloque
- `fee: Optional[float]` - Fee
- `slot: Optional[int]` - Slot
- `confirmation_status: Optional[str]` - Estado de confirmación
- `created_at: datetime` - Fecha de creación
- `confirmed_at: Optional[datetime]` - Fecha de confirmación
- `metadata: Optional[Dict[str, Any]]` - Metadatos

#### `TokenBalanceRecord`
**Propósito**: Registro de balance de token.

**Atributos**:
- `user_id: str` - ID del usuario
- `token_mint: str` - Mint del token
- `balance: int` - Balance
- `last_updated: datetime` - Última actualización
- `transaction_count: int = 0` - Número de transacciones

#### `SPLDataPersistence`
**Propósito**: Persistencia de datos SPL.

**Métodos principales**:
- `__init__(db_path: str = "shaili_ai/data/spl_database.db")` - Inicializar
- `_init_database()` - Inicializar base de datos
- `_get_connection()` - Obtener conexión
- `save_token_account(account: TokenAccountRecord) -> bool` - Guardar cuenta de token
- `get_token_account(user_id: str) -> Optional[TokenAccountRecord]` - Obtener cuenta de token
- `update_token_balance(user_id: str, new_balance: int, token_mint: str) -> bool` - Actualizar balance
- `save_transaction(transaction: TransactionRecord) -> bool` - Guardar transacción
- `get_transaction(transaction_id: str) -> Optional[TransactionRecord]` - Obtener transacción
- `get_user_transactions(user_id: str, limit: int = 50) -> List[TransactionRecord]` - Obtener transacciones de usuario
- `get_user_balance(user_id: str, token_mint: str) -> Optional[TokenBalanceRecord]` - Obtener balance de usuario
- `update_transaction_status(transaction_id: str, status: str, signature: Optional[str] = None, block_height: Optional[int] = None, fee: Optional[float] = None, slot: Optional[int] = None, confirmation_status: Optional[str] = None) -> bool` - Actualizar estado de transacción
- `save_token_statistics(token_mint: str, total_supply: int, circulating_supply: int, burned_supply: int, total_accounts: int, total_transactions: int) -> bool` - Guardar estadísticas de token
- `get_token_statistics(token_mint: str) -> Optional[Dict[str, Any]]` - Obtener estadísticas de token
- `get_transaction_summary(days: int = 30) -> Dict[str, Any]` - Obtener resumen de transacciones
- `backup_database(backup_path: str) -> bool` - Hacer backup de base de datos

**Ejemplo de uso**:
```python
from modules.blockchain.spl_data_persistence import (
    SPLDataPersistence, TokenAccountRecord, TransactionRecord
)

# Inicializar persistencia
persistence = SPLDataPersistence()

# Guardar cuenta de token
account_record = TokenAccountRecord(
    user_id="usuario1",
    token_account="account123",
    mint_address="mint456",
    balance=1000
)
persistence.save_token_account(account_record)

# Guardar transacción
transaction_record = TransactionRecord(
    transaction_id="tx789",
    from_user="usuario1",
    to_user="usuario2",
    amount=100,
    token_mint="SHEILY",
    transaction_type="transfer",
    reason="payment",
    status="confirmed"
)
persistence.save_transaction(transaction_record)

# Obtener balance
balance = persistence.get_user_balance("usuario1", "SHEILY")
print(f"Balance: {balance.balance if balance else 0}")

# Obtener transacciones
transactions = persistence.get_user_transactions("usuario1", limit=10)
for tx in transactions:
    print(f"Transacción: {tx.transaction_id} - {tx.amount} {tx.token_mint}")

# Obtener estadísticas
stats = persistence.get_token_statistics("SHEILY")
if stats:
    print(f"Supply total: {stats['total_supply']}")
    print(f"Supply circulante: {stats['circulating_supply']}")
```

## 🔄 Flujo de Trabajo de Blockchain

### 1. Configuración Inicial
```python
from modules.blockchain.solana_blockchain_real import SolanaBlockchainReal, SolanaConfig
from modules.blockchain.secure_key_management import SecureKeyManagement

# Configurar Solana
config = SolanaConfig(network="devnet")
blockchain = SolanaBlockchainReal(config)

# Configurar gestión de claves
key_manager = SecureKeyManagement()
```

### 2. Creación de Wallets
```python
# Crear wallet para usuario
wallet = blockchain.create_wallet("usuario1")
secure_wallet = key_manager.create_user_wallet("usuario1", "password123")
```

### 3. Gestión de Tokens
```python
from modules.blockchain.sheily_spl_real import SheilySPLReal

spl_real = SheilySPLReal()

# Crear cuenta de token
account = spl_real.create_real_user_token_account("usuario1")

# Mintear tokens
transaction = spl_real.mint_real_tokens("usuario1", 1000, "reward")

# Transferir tokens
transfer = spl_real.transfer_real_tokens("usuario1", "usuario2", 100)
```

### 4. Monitoreo y Seguridad
```python
from modules.blockchain.rate_limiter import RateLimiter
from modules.blockchain.transaction_monitor import TransactionMonitor

# Configurar rate limiting
rate_limiter = RateLimiter()
allowed, _ = rate_limiter.check_rate_limit("usuario1", "api_requests")

# Configurar monitoreo
monitor = TransactionMonitor()
monitor.enable_monitoring()
```

### 5. Persistencia de Datos
```python
from modules.blockchain.spl_data_persistence import SPLDataPersistence

persistence = SPLDataPersistence()

# Guardar datos
persistence.save_token_account(account_record)
persistence.save_transaction(transaction_record)

# Obtener datos
balance = persistence.get_user_balance("usuario1", "SHEILY")
transactions = persistence.get_user_transactions("usuario1")
```

## 🚨 Manejo de Errores

### Errores Comunes en Blockchain

1. **Error de conexión**
   ```python
   # Error: ConnectionError
   # Solución: Verificar RPC URL y conexión de red
   blockchain = SolanaBlockchainReal(config)
   ```

2. **Error de clave privada**
   ```python
   # Error: InvalidPrivateKeyError
   # Solución: Verificar formato y encriptación
   keypair = key_manager.get_user_keypair("usuario1", "password")
   ```

3. **Error de transacción**
   ```python
   # Error: TransactionFailedError
   # Solución: Verificar balance y parámetros
   transaction = blockchain.transfer_tokens("usuario1", "usuario2", 100)
   ```

## 📊 Métricas y Monitoreo

### Métricas de Blockchain

1. **Transacciones**
   - Número de transacciones por día
   - Tasa de éxito
   - Tiempo promedio de confirmación
   - Fees promedio

2. **Tokens**
   - Supply total y circulante
   - Número de holders
   - Distribución de balances
   - Actividad de minteo/quema

3. **Rendimiento**
   - Tiempo de respuesta de RPC
   - Uso de memoria
   - Errores de conexión
   - Rate limiting

### Ejemplo de Monitoreo

```python
# Obtener métricas de transacciones
metrics = monitor.get_transaction_metrics()
print(f"Transacciones confirmadas: {metrics['confirmed_transactions']}")
print(f"Transacciones fallidas: {metrics['failed_transactions']}")

# Obtener estadísticas de token
stats = spl_real.get_real_token_statistics()
print(f"Supply total: {stats['total_supply']}")
print(f"Holders: {stats['total_holders']}")

# Obtener métricas de rate limiting
rate_stats = rate_limiter.get_system_stats()
print(f"Requests totales: {rate_stats['total_requests']}")
print(f"Violaciones: {rate_stats['total_violations']}")
```

Esta documentación proporciona una visión completa de todos los módulos de blockchain, incluyendo sus clases, métodos, ejemplos de uso y mejores prácticas para el desarrollo de sistemas blockchain basados en Solana.
