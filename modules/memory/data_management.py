import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserData(Base):
    __tablename__ = "user_data"

    id = sa.Column(sa.String, primary_key=True)
    user_id = sa.Column(sa.String)
    domain = sa.Column(sa.String)
    data_type = sa.Column(sa.String)
    content = sa.Column(sa.Text)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    is_pii = sa.Column(sa.Boolean, default=False)
    retention_period = sa.Column(sa.Integer, default=90)


class DeletionLog(Base):
    __tablename__ = "deletion_log"

    id = sa.Column(sa.String, primary_key=True)
    user_id = sa.Column(sa.String)
    deletion_type = sa.Column(sa.String)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    reason = sa.Column(sa.Text)


class DataManagementService:
    def __init__(
        self,
        db_url: str = "postgresql://user:password@localhost/sheily_db",
        log_dir: str = "logs/data_management",
    ):
        """
        Servicio de gestión de datos con soporte para borrado selectivo y GDPR

        Args:
            db_url (str): URL de conexión a PostgreSQL
            log_dir (str): Directorio para logs de auditoría
        """
        # Configurar logging
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            handlers=[
                logging.FileHandler(f"{log_dir}/data_management.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

        # Conexión a base de datos
        self.engine = sa.create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store_user_data(
        self,
        user_id: str,
        data: Dict[str, Any],
        domain: str,
        data_type: str,
        is_pii: bool = False,
        retention_period: int = 90,
    ):
        """
        Almacenar datos de usuario con metadatos de privacidad
        """
        # Generar ID único
        data_id = hashlib.sha256(
            f"{user_id}_{domain}_{data_type}_{datetime.now()}".encode()
        ).hexdigest()

        # Serializar datos
        content = json.dumps(data, ensure_ascii=False)

        # Insertar en base de datos
        session = self.Session()
        try:
            user_data = UserData(
                id=data_id,
                user_id=user_id,
                domain=domain,
                data_type=data_type,
                content=content,
                is_pii=is_pii,
                retention_period=retention_period,
            )
            session.add(user_data)
            session.commit()

            self.logger.info(f"Datos almacenados: {data_id} (PII: {is_pii})")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error almacenando datos: {e}")
        finally:
            session.close()

    def delete_user_data(
        self,
        user_id: str,
        domain: Optional[str] = None,
        data_type: Optional[str] = None,
        reason: str = "Solicitud de usuario",
    ):
        """
        Borrado selectivo de datos de usuario
        """
        session = self.Session()
        try:
            # Construir consulta
            query = session.query(UserData).filter(UserData.user_id == user_id)
            if domain:
                query = query.filter(UserData.domain == domain)
            if data_type:
                query = query.filter(UserData.data_type == data_type)

            # Contar y eliminar registros
            deleted_count = query.count()
            query.delete(synchronize_session=False)

            # Registrar borrado en log de auditoría
            deletion_id = hashlib.sha256(
                f"{user_id}_{datetime.now()}".encode()
            ).hexdigest()

            deletion_log = DeletionLog(
                id=deletion_id,
                user_id=user_id,
                deletion_type=f"{'Dominio' if domain else 'Total'}",
                reason=reason,
            )
            session.add(deletion_log)

            session.commit()

            self.logger.info(f"Borrado de datos: {deleted_count} registros eliminados")
            return deleted_count
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error borrando datos: {e}")
            return 0
        finally:
            session.close()

    def export_user_data(self, user_id: str, export_format: str = "jsonl") -> str:
        """
        Exportar datos de usuario
        """
        session = self.Session()
        try:
            # Consultar datos del usuario
            user_data = (
                session.query(UserData).filter(UserData.user_id == user_id).all()
            )

            # Definir ruta de exportación
            export_dir = "exports/user_data"
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(
                export_dir,
                f"{user_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}",
            )

            # Exportar según formato
            if export_format == "jsonl":
                with open(export_path, "w", encoding="utf-8") as f:
                    for row in user_data:
                        export_entry = {
                            "id": row.id,
                            "domain": row.domain,
                            "data_type": row.data_type,
                            "content": json.loads(row.content),
                            "timestamp": row.timestamp.isoformat(),
                            "is_pii": row.is_pii,
                        }
                        json.dump(export_entry, f, ensure_ascii=False)
                        f.write("\n")

            self.logger.info(f"Datos exportados: {export_path}")
            return export_path
        except Exception as e:
            self.logger.error(f"Error exportando datos: {e}")
            return ""
        finally:
            session.close()

    def cleanup_expired_data(self):
        """
        Eliminar datos expirados según política de retención
        """
        session = self.Session()
        try:
            # Calcular fecha de expiración
            expiration_date = datetime.now() - timedelta(days=90)

            # Eliminar datos expirados
            deleted_count = (
                session.query(UserData)
                .filter(UserData.timestamp < expiration_date)
                .delete(synchronize_session=False)
            )

            session.commit()

            self.logger.info(
                f"Limpieza de datos: {deleted_count} registros expirados eliminados"
            )
            return deleted_count
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error limpiando datos expirados: {e}")
            return 0
        finally:
            session.close()
