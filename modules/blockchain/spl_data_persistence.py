#!/usr/bin/env python3
"""
Sistema de Persistencia de Datos para SPL
========================================
Almacenamiento persistente de transacciones, cuentas y balances
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class TokenAccountRecord:
    """Registro de cuenta de token"""

    user_id: str
    token_account: str
    associated_token_account: Optional[str]
    mint_address: str
    balance: int
    created_at: datetime
    last_updated: datetime
    is_active: bool = True


@dataclass
class TransactionRecord:
    """Registro de transacción"""

    transaction_id: str
    signature: Optional[str]
    from_user: str
    to_user: str
    amount: int
    token_mint: str
    transaction_type: str  # 'mint', 'transfer', 'burn'
    reason: str
    status: str
    block_height: Optional[int]
    fee: Optional[float]
    slot: Optional[int]
    confirmation_status: Optional[str]
    created_at: datetime
    confirmed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TokenBalanceRecord:
    """Registro de balance de token"""

    user_id: str
    token_mint: str
    balance: int
    last_updated: datetime
    transaction_count: int = 0


class SPLDataPersistence:
    """Sistema de persistencia de datos para SPL"""

    def __init__(self, db_path: str = "shaili_ai/data/spl_database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

        # Inicializar base de datos
        self._init_database()

        logger.info(f"🗄️ Sistema de persistencia SPL inicializado: {self.db_path}")

    def _init_database(self):
        """Inicializar base de datos"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de cuentas de token
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS token_accounts (
                    user_id TEXT PRIMARY KEY,
                    token_account TEXT NOT NULL,
                    associated_token_account TEXT,
                    mint_address TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1
                )
            """
            )

            # Tabla de transacciones
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    signature TEXT,
                    from_user TEXT NOT NULL,
                    to_user TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    token_mint TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    block_height INTEGER,
                    fee REAL,
                    slot INTEGER,
                    confirmation_status TEXT,
                    created_at TIMESTAMP NOT NULL,
                    confirmed_at TIMESTAMP,
                    metadata TEXT
                )
            """
            )

            # Tabla de balances
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS token_balances (
                    user_id TEXT,
                    token_mint TEXT,
                    balance INTEGER NOT NULL DEFAULT 0,
                    last_updated TIMESTAMP NOT NULL,
                    transaction_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, token_mint)
                )
            """
            )

            # Tabla de estadísticas
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS token_statistics (
                    token_mint TEXT PRIMARY KEY,
                    total_supply INTEGER NOT NULL,
                    circulating_supply INTEGER NOT NULL,
                    burned_supply INTEGER NOT NULL,
                    total_accounts INTEGER NOT NULL,
                    total_transactions INTEGER NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                )
            """
            )

            # Índices para optimizar consultas
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(from_user, to_user)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_created ON transactions(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_balances_user ON token_balances(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_balances_mint ON token_balances(token_mint)"
            )

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def save_token_account(self, account: TokenAccountRecord) -> bool:
        """Guardar cuenta de token"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO token_accounts 
                        (user_id, token_account, associated_token_account, mint_address, 
                         balance, created_at, last_updated, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            account.user_id,
                            account.token_account,
                            account.associated_token_account,
                            account.mint_address,
                            account.balance,
                            account.created_at.isoformat(),
                            account.last_updated.isoformat(),
                            account.is_active,
                        ),
                    )

                    conn.commit()

                    logger.info(f"✅ Cuenta de token guardada: {account.user_id}")
                    return True

        except Exception as e:
            logger.error(f"❌ Error guardando cuenta de token: {e}")
            return False

    def get_token_account(self, user_id: str) -> Optional[TokenAccountRecord]:
        """Obtener cuenta de token"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM token_accounts WHERE user_id = ? AND is_active = 1
                """,
                    (user_id,),
                )

                row = cursor.fetchone()
                if row:
                    return TokenAccountRecord(
                        user_id=row["user_id"],
                        token_account=row["token_account"],
                        associated_token_account=row["associated_token_account"],
                        mint_address=row["mint_address"],
                        balance=row["balance"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        last_updated=datetime.fromisoformat(row["last_updated"]),
                        is_active=bool(row["is_active"]),
                    )
                return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo cuenta de token: {e}")
            return None

    def update_token_balance(
        self, user_id: str, new_balance: int, token_mint: str
    ) -> bool:
        """Actualizar balance de token"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    now = datetime.now()

                    # Actualizar cuenta de token
                    cursor.execute(
                        """
                        UPDATE token_accounts 
                        SET balance = ?, last_updated = ?
                        WHERE user_id = ? AND mint_address = ?
                    """,
                        (new_balance, now.isoformat(), user_id, token_mint),
                    )

                    # Actualizar balance
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO token_balances 
                        (user_id, token_mint, balance, last_updated, transaction_count)
                        VALUES (?, ?, ?, ?, 
                            COALESCE((SELECT transaction_count FROM token_balances 
                                     WHERE user_id = ? AND token_mint = ?), 0) + 1)
                    """,
                        (
                            user_id,
                            token_mint,
                            new_balance,
                            now.isoformat(),
                            user_id,
                            token_mint,
                        ),
                    )

                    conn.commit()

                    logger.info(f"✅ Balance actualizado: {user_id} = {new_balance}")
                    return True

        except Exception as e:
            logger.error(f"❌ Error actualizando balance: {e}")
            return False

    def save_transaction(self, transaction: TransactionRecord) -> bool:
        """Guardar transacción"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO transactions 
                        (transaction_id, signature, from_user, to_user, amount, token_mint,
                         transaction_type, reason, status, block_height, fee, slot,
                         confirmation_status, created_at, confirmed_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            transaction.transaction_id,
                            transaction.signature,
                            transaction.from_user,
                            transaction.to_user,
                            transaction.amount,
                            transaction.token_mint,
                            transaction.transaction_type,
                            transaction.reason,
                            transaction.status,
                            transaction.block_height,
                            transaction.fee,
                            transaction.slot,
                            transaction.confirmation_status,
                            transaction.created_at.isoformat(),
                            (
                                transaction.confirmed_at.isoformat()
                                if transaction.confirmed_at
                                else None
                            ),
                            (
                                json.dumps(transaction.metadata)
                                if transaction.metadata
                                else None
                            ),
                        ),
                    )

                    conn.commit()

                    logger.info(
                        f"✅ Transacción guardada: {transaction.transaction_id}"
                    )
                    return True

        except Exception as e:
            logger.error(f"❌ Error guardando transacción: {e}")
            return False

    def get_transaction(self, transaction_id: str) -> Optional[TransactionRecord]:
        """Obtener transacción"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM transactions WHERE transaction_id = ?
                """,
                    (transaction_id,),
                )

                row = cursor.fetchone()
                if row:
                    return TransactionRecord(
                        transaction_id=row["transaction_id"],
                        signature=row["signature"],
                        from_user=row["from_user"],
                        to_user=row["to_user"],
                        amount=row["amount"],
                        token_mint=row["token_mint"],
                        transaction_type=row["transaction_type"],
                        reason=row["reason"],
                        status=row["status"],
                        block_height=row["block_height"],
                        fee=row["fee"],
                        slot=row["slot"],
                        confirmation_status=row["confirmation_status"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        confirmed_at=(
                            datetime.fromisoformat(row["confirmed_at"])
                            if row["confirmed_at"]
                            else None
                        ),
                        metadata=(
                            json.loads(row["metadata"]) if row["metadata"] else None
                        ),
                    )
                return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo transacción: {e}")
            return None

    def get_user_transactions(
        self, user_id: str, limit: int = 50
    ) -> List[TransactionRecord]:
        """Obtener transacciones de usuario"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM transactions 
                    WHERE from_user = ? OR to_user = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (user_id, user_id, limit),
                )

                transactions = []
                for row in cursor.fetchall():
                    transactions.append(
                        TransactionRecord(
                            transaction_id=row["transaction_id"],
                            signature=row["signature"],
                            from_user=row["from_user"],
                            to_user=row["to_user"],
                            amount=row["amount"],
                            token_mint=row["token_mint"],
                            transaction_type=row["transaction_type"],
                            reason=row["reason"],
                            status=row["status"],
                            block_height=row["block_height"],
                            fee=row["fee"],
                            slot=row["slot"],
                            confirmation_status=row["confirmation_status"],
                            created_at=datetime.fromisoformat(row["created_at"]),
                            confirmed_at=(
                                datetime.fromisoformat(row["confirmed_at"])
                                if row["confirmed_at"]
                                else None
                            ),
                            metadata=(
                                json.loads(row["metadata"]) if row["metadata"] else None
                            ),
                        )
                    )

                return transactions

        except Exception as e:
            logger.error(f"❌ Error obteniendo transacciones de usuario: {e}")
            return []

    def get_user_balance(
        self, user_id: str, token_mint: str
    ) -> Optional[TokenBalanceRecord]:
        """Obtener balance de usuario"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM token_balances 
                    WHERE user_id = ? AND token_mint = ?
                """,
                    (user_id, token_mint),
                )

                row = cursor.fetchone()
                if row:
                    return TokenBalanceRecord(
                        user_id=row["user_id"],
                        token_mint=row["token_mint"],
                        balance=row["balance"],
                        last_updated=datetime.fromisoformat(row["last_updated"]),
                        transaction_count=row["transaction_count"],
                    )
                return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo balance de usuario: {e}")
            return None

    def update_transaction_status(
        self,
        transaction_id: str,
        status: str,
        signature: Optional[str] = None,
        block_height: Optional[int] = None,
        fee: Optional[float] = None,
        slot: Optional[int] = None,
        confirmation_status: Optional[str] = None,
    ) -> bool:
        """Actualizar estado de transacción"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    now = datetime.now()

                    cursor.execute(
                        """
                        UPDATE transactions 
                        SET status = ?, signature = ?, block_height = ?, fee = ?, 
                            slot = ?, confirmation_status = ?, confirmed_at = ?
                        WHERE transaction_id = ?
                    """,
                        (
                            status,
                            signature,
                            block_height,
                            fee,
                            slot,
                            confirmation_status,
                            now.isoformat(),
                            transaction_id,
                        ),
                    )

                    conn.commit()

                    logger.info(
                        f"✅ Estado de transacción actualizado: {transaction_id} = {status}"
                    )
                    return True

        except Exception as e:
            logger.error(f"❌ Error actualizando estado de transacción: {e}")
            return False

    def save_token_statistics(
        self,
        token_mint: str,
        total_supply: int,
        circulating_supply: int,
        burned_supply: int,
        total_accounts: int,
        total_transactions: int,
    ) -> bool:
        """Guardar estadísticas del token"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    now = datetime.now()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO token_statistics 
                        (token_mint, total_supply, circulating_supply, burned_supply,
                         total_accounts, total_transactions, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            token_mint,
                            total_supply,
                            circulating_supply,
                            burned_supply,
                            total_accounts,
                            total_transactions,
                            now.isoformat(),
                        ),
                    )

                    conn.commit()

                    logger.info(f"✅ Estadísticas guardadas para {token_mint}")
                    return True

        except Exception as e:
            logger.error(f"❌ Error guardando estadísticas: {e}")
            return False

    def get_token_statistics(self, token_mint: str) -> Optional[Dict[str, Any]]:
        """Obtener estadísticas del token"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM token_statistics WHERE token_mint = ?
                """,
                    (token_mint,),
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "token_mint": row["token_mint"],
                        "total_supply": row["total_supply"],
                        "circulating_supply": row["circulating_supply"],
                        "burned_supply": row["burned_supply"],
                        "total_accounts": row["total_accounts"],
                        "total_transactions": row["total_transactions"],
                        "last_updated": datetime.fromisoformat(row["last_updated"]),
                    }
                return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return None

    def get_transaction_summary(self, days: int = 30) -> Dict[str, Any]:
        """Obtener resumen de transacciones"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                since_date = datetime.now() - timedelta(days=days)

                # Total de transacciones
                cursor.execute(
                    """
                    SELECT COUNT(*) as total FROM transactions 
                    WHERE created_at >= ?
                """,
                    (since_date.isoformat(),),
                )
                total_transactions = cursor.fetchone()["total"]

                # Transacciones por tipo
                cursor.execute(
                    """
                    SELECT transaction_type, COUNT(*) as count FROM transactions 
                    WHERE created_at >= ?
                    GROUP BY transaction_type
                """,
                    (since_date.isoformat(),),
                )
                transactions_by_type = {
                    row["transaction_type"]: row["count"] for row in cursor.fetchall()
                }

                # Transacciones por estado
                cursor.execute(
                    """
                    SELECT status, COUNT(*) as count FROM transactions 
                    WHERE created_at >= ?
                    GROUP BY status
                """,
                    (since_date.isoformat(),),
                )
                transactions_by_status = {
                    row["status"]: row["count"] for row in cursor.fetchall()
                }

                # Total de fees
                cursor.execute(
                    """
                    SELECT SUM(fee) as total_fees FROM transactions 
                    WHERE created_at >= ? AND fee IS NOT NULL
                """,
                    (since_date.isoformat(),),
                )
                total_fees = cursor.fetchone()["total_fees"] or 0

                return {
                    "period_days": days,
                    "total_transactions": total_transactions,
                    "transactions_by_type": transactions_by_type,
                    "transactions_by_status": transactions_by_status,
                    "total_fees": total_fees,
                    "since_date": since_date.isoformat(),
                }

        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen de transacciones: {e}")
            return {}

    def backup_database(self, backup_path: str) -> bool:
        """Crear backup de la base de datos"""
        try:
            import shutil

            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(self.db_path, backup_file)

            logger.info(f"✅ Backup creado: {backup_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False


# Instancia global
_spl_persistence: Optional[SPLDataPersistence] = None


def get_spl_persistence() -> SPLDataPersistence:
    """Obtener instancia global del sistema de persistencia"""
    global _spl_persistence

    if _spl_persistence is None:
        _spl_persistence = SPLDataPersistence()

    return _spl_persistence
