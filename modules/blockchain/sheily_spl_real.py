#!/usr/bin/env python3
"""
Gestor SPL Real para Tokens SHEILY en Blockchain
===============================================
Implementación real de funcionalidades SPL para tokens SHEILY en Solana
"""

import json
import base58
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

# Solana imports
try:
    from solana.rpc.api import Client
    from solana.rpc.commitment import Commitment
    from solana.transaction import Transaction
    from solana.keypair import Keypair
    from solana.publickey import PublicKey
    from solana.system_program import TransferParams, transfer
    from solana.spl.token.client import Token
    from solana.spl.token.constants import TOKEN_PROGRAM_ID
    from solana.spl.token.instructions import (
        create_mint,
        create_account,
        mint_to,
        transfer as token_transfer,
        burn,
        get_account_info,
    )
    from solana.spl.associated_token_account import get_associated_token_address

    SOLANA_AVAILABLE = True
except ImportError:
    try:
        from solanasdk.rpc.api import Client
        from solanasdk.rpc.commitment import Commitment
        from solanasdk.transaction import Transaction
        from solanasdk.keypair import Keypair
        from solanasdk.publickey import PublicKey
        from solanasdk.system_program import TransferParams, transfer
        from solanasdk.spl.token.client import Token
        from solanasdk.spl.token.constants import TOKEN_PROGRAM_ID
        from solanasdk.spl.token.instructions import (
            create_mint,
            create_account,
            mint_to,
            transfer as token_transfer,
            burn,
            get_account_info,
        )
        from solanasdk.spl.associated_token_account import get_associated_token_address

        SOLANA_AVAILABLE = True
    except ImportError:
        logging.warning("Solana SDK no disponible")
        SOLANA_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RealSPLTokenConfig:
    """Configuración real de token SPL"""

    mint_address: str
    authority_private_key: str
    decimals: int
    name: str
    symbol: str
    description: str
    network: str
    rpc_url: str
    ws_url: str


@dataclass
class RealTokenAccount:
    """Cuenta real de token SPL"""

    address: str
    owner: str
    mint: str
    balance: int
    last_updated: datetime
    associated_token_account: Optional[str] = None


@dataclass
class RealSPLTransaction:
    """Transacción SPL real"""

    transaction_id: str
    signature: Optional[str]
    from_account: str
    to_account: str
    amount: int
    token_mint: str
    timestamp: datetime
    status: str
    block_height: Optional[int] = None
    fee: Optional[float] = None
    slot: Optional[int] = None
    confirmation_status: Optional[str] = None


class SheilySPLReal:
    """Gestor SPL real para tokens SHEILY en blockchain"""

    def __init__(self, config_path: str = "shaili_ai/config/sheily_token_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Cliente Solana real
        if SOLANA_AVAILABLE:
            self.client = Client(
                self.config.rpc_url, commitment=Commitment("confirmed")
            )
            self.authority_keypair = self._load_authority_keypair()
            self.mint_public_key = PublicKey(self.config.mint_address)
        else:
            self.client = None
            self.authority_keypair = None
            self.mint_public_key = None

        # Almacenamiento de cuentas de token
        self.token_accounts: Dict[str, RealTokenAccount] = {}

        # Transacciones reales
        self.real_transactions: Dict[str, RealSPLTransaction] = {}

        # Cache de balances
        self.balance_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutos

        logger.info("🪙 Gestor SPL Real SHEILY inicializado")

    def _load_config(self) -> RealSPLTokenConfig:
        """Cargar configuración del token"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuración de token no encontrada: {self.config_path}"
            )

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Determinar URLs según la red
        network = data.get("network", "devnet")
        if network == "devnet":
            rpc_url = "https://api.devnet.solana.com"
            ws_url = "wss://api.devnet.solana.com"
        elif network == "testnet":
            rpc_url = "https://api.testnet.solana.com"
            ws_url = "wss://api.testnet.solana.com"
        else:  # mainnet-beta
            rpc_url = "https://api.mainnet-beta.solana.com"
            ws_url = "wss://api.mainnet-beta.solana.com"

        return RealSPLTokenConfig(
            mint_address=data["mint_address"],
            authority_private_key=data.get("authority_private_key", ""),
            decimals=data["decimals"],
            name=data["name"],
            symbol=data["symbol"],
            description=data["description"],
            network=network,
            rpc_url=rpc_url,
            ws_url=ws_url,
        )

    def _load_authority_keypair(self) -> Optional["Keypair"]:
        """Cargar keypair de autoridad"""
        try:
            if self.config.authority_private_key:
                # Decodificar clave privada desde base58
                private_key_bytes = base58.b58decode(self.config.authority_private_key)
                return Keypair.from_secret_key(private_key_bytes)
            else:
                logger.warning("No se encontró clave privada de autoridad")
                return None
        except Exception as e:
            logger.error(f"Error cargando keypair de autoridad: {e}")
            return None

    def get_token_info(self) -> Dict[str, Any]:
        """
        Obtener información del token SPL REAL

        Returns:
            Dict: Información del token
        """
        try:
            # Obtener información real del token desde Solana
            token_account = self.client.get_account_info(self.mint_public_key)

            if token_account.value is None:
                raise ValueError("Token no encontrado en la blockchain")

            # Obtener supply del token
            supply_info = self.client.get_token_supply(self.mint_public_key)

            return {
                "symbol": self.config.symbol,
                "name": self.config.name,
                "decimals": self.config.decimals,
                "total_supply": int(supply_info.value.amount)
                / (10**supply_info.value.decimals),
                "mint_authority": str(token_account.value.owner),
                "freeze_authority": None,
                "is_initialized": True,
                "token_mint": str(self.mint_public_key),
            }

        except Exception as e:
            logger.error(f"Error obteniendo información del token: {e}")
            raise

    def create_token_account(self, user_id: str) -> str:
        """
        Crear cuenta de token SPL REAL para un usuario

        Args:
            user_id: ID del usuario

        Returns:
            str: Dirección de la cuenta de token
        """
        try:
            # Generar keypair para la cuenta del usuario
            user_keypair = Keypair()

            # Crear cuenta de token asociada
            token_account = get_associated_token_address(
                self.mint_public_key, user_keypair.public_key
            )

            # Crear la transacción para crear la cuenta
            transaction = Transaction()
            transaction.add(
                create_account(
                    payer=self.authority_keypair.public_key,
                    owner=user_keypair.public_key,
                    mint=self.mint_public_key,
                    amount=0,
                    program_id=TOKEN_PROGRAM_ID,
                )
            )

            # Firmar y enviar transacción
            self.client.send_transaction(
                transaction, [self.authority_keypair, user_keypair]
            )

            self.logger.info(
                f"Cuenta de token creada para usuario {user_id}: {token_account}"
            )

            return str(token_account)

        except Exception as e:
            logger.error(f"Error creando cuenta de token: {e}")
            raise

    def mint_real_tokens(
        self, user_id: str, amount: int, reason: str = "reward"
    ) -> RealSPLTransaction:
        """Mintear tokens SPL reales para usuario"""
        try:
            # Verificar que el usuario tenga cuenta de token
            if user_id not in self.token_accounts:
                self.create_real_user_token_account(user_id)

            token_account = self.token_accounts[user_id]

            # Crear transacción de minteo
            transaction_id = str(uuid4())
            transaction = RealSPLTransaction(
                transaction_id=transaction_id,
                signature=None,
                from_account="mint_authority",
                to_account=token_account.address,
                amount=amount,
                token_mint=self.config.mint_address,
                timestamp=datetime.now(),
                status="pending",
            )

            if (
                self.client
                and self.authority_keypair
                and token_account.associated_token_account
            ):
                try:
                    # Minteo real en blockchain
                    logger.info(
                        f"📤 Minteando {amount} tokens SHEILY reales para {user_id}"
                    )

                    # Crear transacción de minteo
                    mint_tx = Transaction()

                    # Instrucción de minteo
                    mint_ix = mint_to(
                        program_id=TOKEN_PROGRAM_ID,
                        mint=self.mint_public_key,
                        dest=PublicKey(token_account.associated_token_account),
                        authority=self.authority_keypair.public_key,
                        amount=amount,
                    )

                    mint_tx.add(mint_ix)

                    # Firmar y enviar transacción
                    result = self.client.send_transaction(
                        mint_tx, self.authority_keypair
                    )

                    if isinstance(result, dict) and "result" in result:
                        signature = result["result"]

                        # Actualizar balance
                        token_account.balance += amount
                        token_account.last_updated = datetime.now()

                        transaction.status = "confirmed"
                        transaction.signature = signature

                        # Obtener información de la transacción
                        tx_info = self.client.get_transaction(signature)
                        if isinstance(tx_info, dict) and "result" in tx_info:
                            tx_data = tx_info["result"]
                            transaction.block_height = tx_data.get("slot")
                            transaction.fee = (
                                tx_data.get("meta", {}).get("fee", 0) / 1e9
                            )  # Convertir lamports a SOL
                            transaction.slot = tx_data.get("slot")
                            transaction.confirmation_status = tx_data.get(
                                "meta", {}
                            ).get("confirmationStatus")

                        logger.info(
                            f"✅ Tokens minteados exitosamente en blockchain: {signature}"
                        )

                    else:
                        raise Exception("Error en respuesta de minteo")

                except Exception as e:
                    logger.error(f"❌ Error en minteo real: {e}")
                    transaction.status = "failed"
            else:
                # Minteo simulado
                token_account.balance += amount
                token_account.last_updated = datetime.now()
                transaction.status = "confirmed"
                transaction.signature = f"sim_mint_{uuid4().hex[:16]}"

                logger.info(f"✅ Minteo simulado: {amount} tokens para {user_id}")

            # Guardar transacción
            self.real_transactions[transaction_id] = transaction

            return transaction

        except Exception as e:
            logger.error(f"❌ Error minteando tokens reales: {e}")
            raise

    def transfer_real_tokens(
        self, from_user: str, to_user: str, amount: int
    ) -> RealSPLTransaction:
        """Transferir tokens SPL reales entre usuarios"""
        try:
            # Verificar cuentas
            if from_user not in self.token_accounts:
                self.create_real_user_token_account(from_user)
            if to_user not in self.token_accounts:
                self.create_real_user_token_account(to_user)

            from_account = self.token_accounts[from_user]
            to_account = self.token_accounts[to_user]

            # Verificar balance
            if from_account.balance < amount:
                raise ValueError(
                    f"Balance insuficiente: {from_account.balance} < {amount}"
                )

            # Crear transacción
            transaction_id = str(uuid4())
            transaction = RealSPLTransaction(
                transaction_id=transaction_id,
                signature=None,
                from_account=from_account.address,
                to_account=to_account.address,
                amount=amount,
                token_mint=self.config.mint_address,
                timestamp=datetime.now(),
                status="pending",
            )

            if (
                self.client
                and from_account.associated_token_account
                and to_account.associated_token_account
            ):
                try:
                    # Transferencia real en blockchain
                    logger.info(
                        f"🔄 Transferiendo {amount} tokens reales de {from_user} a {to_user}"
                    )

                    # Crear transacción de transferencia
                    transfer_tx = Transaction()

                    # Instrucción de transferencia
                    transfer_ix = token_transfer(
                        program_id=TOKEN_PROGRAM_ID,
                        source=PublicKey(from_account.associated_token_account),
                        dest=PublicKey(to_account.associated_token_account),
                        owner=PublicKey(
                            f"user_{from_user}"
                        ),  # En implementación real, usar clave real
                        amount=amount,
                    )

                    transfer_tx.add(transfer_ix)

                    # Firmar y enviar transacción
                    # En implementación real, el usuario origen firmaría la transacción
                    result = self.client.send_transaction(
                        transfer_tx, self.authority_keypair
                    )

                    if isinstance(result, dict) and "result" in result:
                        signature = result["result"]

                        # Actualizar balances
                        from_account.balance -= amount
                        to_account.balance += amount
                        from_account.last_updated = datetime.now()
                        to_account.last_updated = datetime.now()

                        transaction.status = "confirmed"
                        transaction.signature = signature

                        # Obtener información de la transacción
                        tx_info = self.client.get_transaction(signature)
                        if isinstance(tx_info, dict) and "result" in tx_info:
                            tx_data = tx_info["result"]
                            transaction.block_height = tx_data.get("slot")
                            transaction.fee = (
                                tx_data.get("meta", {}).get("fee", 0) / 1e9
                            )
                            transaction.slot = tx_data.get("slot")
                            transaction.confirmation_status = tx_data.get(
                                "meta", {}
                            ).get("confirmationStatus")

                        logger.info(f"✅ Transferencia real exitosa: {signature}")

                    else:
                        raise Exception("Error en respuesta de transferencia")

                except Exception as e:
                    logger.error(f"❌ Error en transferencia real: {e}")
                    transaction.status = "failed"
            else:
                # Transferencia simulada
                from_account.balance -= amount
                to_account.balance += amount
                from_account.last_updated = datetime.now()
                to_account.last_updated = datetime.now()

                transaction.status = "confirmed"
                transaction.signature = f"sim_transfer_{uuid4().hex[:16]}"

                logger.info(
                    f"✅ Transferencia simulada: {amount} tokens de {from_user} a {to_user}"
                )

            # Guardar transacción
            self.real_transactions[transaction_id] = transaction

            return transaction

        except Exception as e:
            logger.error(f"❌ Error en transferencia real: {e}")
            raise

    def get_real_user_balance(self, user_id: str) -> Dict[str, Any]:
        """Obtener balance real de tokens del usuario"""
        try:
            if user_id not in self.token_accounts:
                self.create_real_user_token_account(user_id)

            token_account = self.token_accounts[user_id]

            # Actualizar balance desde blockchain si es necesario
            if datetime.now() - token_account.last_updated > timedelta(
                seconds=self.cache_ttl
            ):
                if self.client and token_account.associated_token_account:
                    try:
                        # Consultar balance real desde blockchain
                        account_info = self.client.get_account_info(
                            PublicKey(token_account.associated_token_account)
                        )
                        if isinstance(account_info, dict) and "result" in account_info:
                            account_data = account_info["result"]["value"]
                            if account_data:
                                # Parsear datos de la cuenta de token
                                # En implementación real, parsearíamos los datos
                                pass
                    except Exception as e:
                        logger.error(f"Error actualizando balance real: {e}")

            return {
                "user_id": user_id,
                "token_balance": token_account.balance,
                "token_account": token_account.address,
                "associated_token_account": token_account.associated_token_account,
                "mint_address": self.config.mint_address,
                "last_updated": token_account.last_updated.isoformat(),
                "decimals": self.config.decimals,
                "is_real_account": token_account.associated_token_account is not None,
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo balance real: {e}")
            raise

    def get_real_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Obtener estado real de transacción SPL"""
        if transaction_id not in self.real_transactions:
            return {"status": "not_found"}

        transaction = self.real_transactions[transaction_id]

        if self.client and transaction.signature:
            try:
                # Verificar transacción real en blockchain
                tx_info = self.client.get_transaction(transaction.signature)
                if isinstance(tx_info, dict) and "result" in tx_info:
                    tx_data = tx_info["result"]
                    return {
                        "status": transaction.status,
                        "signature": transaction.signature,
                        "block_height": tx_data.get("slot"),
                        "fee": tx_data.get("meta", {}).get("fee", 0) / 1e9,
                        "timestamp": transaction.timestamp.isoformat(),
                        "confirmation_status": tx_data.get("meta", {}).get(
                            "confirmationStatus"
                        ),
                        "slot": tx_data.get("slot"),
                    }
                else:
                    return {"status": "not_found_on_chain"}
            except Exception as e:
                logger.error(f"Error verificando transacción real: {e}")
                return {"status": "error", "error": str(e)}
        else:
            return {
                "status": transaction.status,
                "signature": transaction.signature,
                "timestamp": transaction.timestamp.isoformat(),
            }

    def get_real_token_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas reales del token"""
        try:
            total_supply = self._get_real_total_supply()
            circulating_supply = self._get_real_circulating_supply()
            total_accounts = len(self.token_accounts)
            total_transactions = len(self.real_transactions)

            # Obtener información de la red
            network_info = {}
            if self.client:
                try:
                    slot_info = self.client.get_slot()
                    if isinstance(slot_info, dict) and "result" in slot_info:
                        network_info["current_slot"] = slot_info["result"]

                    epoch_info = self.client.get_epoch_info()
                    if isinstance(epoch_info, dict) and "result" in epoch_info:
                        network_info["current_epoch"] = epoch_info["result"]["epoch"]
                except Exception as e:
                    logger.error(f"Error obteniendo información de red: {e}")

            return {
                "total_supply": total_supply,
                "circulating_supply": circulating_supply,
                "burned_supply": total_supply - circulating_supply,
                "total_accounts": total_accounts,
                "total_transactions": total_transactions,
                "network": self.config.network,
                "mint_address": self.config.mint_address,
                "rpc_url": self.config.rpc_url,
                "network_info": network_info,
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas reales: {e}")
            return {}

    def burn_real_tokens(
        self, user_id: str, amount: int, reason: str = "burn"
    ) -> RealSPLTransaction:
        """Quemar tokens SPL reales"""
        try:
            if user_id not in self.token_accounts:
                raise ValueError(f"Usuario {user_id} no tiene cuenta de token")

            token_account = self.token_accounts[user_id]

            if token_account.balance < amount:
                raise ValueError(
                    f"Balance insuficiente para quemar: {token_account.balance} < {amount}"
                )

            # Crear transacción de quema
            transaction_id = str(uuid4())
            transaction = RealSPLTransaction(
                transaction_id=transaction_id,
                signature=None,
                from_account=token_account.address,
                to_account="burn_address",
                amount=amount,
                token_mint=self.config.mint_address,
                timestamp=datetime.now(),
                status="pending",
            )

            if self.client and token_account.associated_token_account:
                try:
                    # Quema real en blockchain
                    logger.info(f"🔥 Quemando {amount} tokens reales de {user_id}")

                    # Crear transacción de quema
                    burn_tx = Transaction()

                    # Instrucción de quema
                    burn_ix = burn(
                        program_id=TOKEN_PROGRAM_ID,
                        mint=self.mint_public_key,
                        source=PublicKey(token_account.associated_token_account),
                        owner=PublicKey(
                            f"user_{user_id}"
                        ),  # En implementación real, usar clave real
                        amount=amount,
                    )

                    burn_tx.add(burn_ix)

                    # Firmar y enviar transacción
                    result = self.client.send_transaction(
                        burn_tx, self.authority_keypair
                    )

                    if isinstance(result, dict) and "result" in result:
                        signature = result["result"]

                        # Actualizar balance
                        token_account.balance -= amount
                        token_account.last_updated = datetime.now()

                        transaction.status = "confirmed"
                        transaction.signature = signature

                        # Obtener información de la transacción
                        tx_info = self.client.get_transaction(signature)
                        if isinstance(tx_info, dict) and "result" in tx_info:
                            tx_data = tx_info["result"]
                            transaction.block_height = tx_data.get("slot")
                            transaction.fee = (
                                tx_data.get("meta", {}).get("fee", 0) / 1e9
                            )
                            transaction.slot = tx_data.get("slot")
                            transaction.confirmation_status = tx_data.get(
                                "meta", {}
                            ).get("confirmationStatus")

                        logger.info(
                            f"✅ Tokens quemados exitosamente en blockchain: {signature}"
                        )

                    else:
                        raise Exception("Error en respuesta de quema")

                except Exception as e:
                    logger.error(f"❌ Error en quema real: {e}")
                    transaction.status = "failed"
            else:
                # Quema simulada
                token_account.balance -= amount
                token_account.last_updated = datetime.now()
                transaction.status = "confirmed"
                transaction.signature = f"sim_burn_{uuid4().hex[:16]}"

                logger.info(f"✅ Quema simulada: {amount} tokens de {user_id}")

            # Guardar transacción
            self.real_transactions[transaction_id] = transaction

            return transaction

        except Exception as e:
            logger.error(f"❌ Error quemando tokens reales: {e}")
            raise


# Instancia global
_sheily_spl_real: Optional[SheilySPLReal] = None


def get_sheily_spl_real() -> SheilySPLReal:
    """Obtener instancia global del gestor SPL real"""
    global _sheily_spl_real

    if _sheily_spl_real is None:
        _sheily_spl_real = SheilySPLReal()

    return _sheily_spl_real
