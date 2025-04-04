# ¡Este es mi servicio de datos!
# Me encargué de hacer todas las consultas lo más eficientes posible

import logging
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime
from datetime import datetime
from ..config.settings import DB_CONFIG, LOG_CONFIG, CACHE_CONFIG

# Los logs son nuestros amigos
# Me han salvado de muchos problemas
logging.basicConfig(
    level=LOG_CONFIG["level"],
    format=LOG_CONFIG["format"]
)
logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        """¡Hola! Este es el constructor del servicio.
        
        Me costó un poco configurar bien la conexión a la base de datos.
        El pool_size lo ajusté después de ver que se saturaba con muchas conexiones.
        """
        try:
            self.engine = create_engine(
                DB_CONFIG["url"],
                pool_size=DB_CONFIG["pool_size"],
                max_overflow=DB_CONFIG["max_overflow"],
                echo=DB_CONFIG["echo"]
            )
            self.metadata = MetaData()
            self.cache = {} if CACHE_CONFIG["enabled"] else None
            self._create_control_table()
            logger.info("¡Conexión exitosa a la base de datos!")
        except Exception as e:
            logger.error(f"¡Ups! No pude conectar a la base de datos: {str(e)}")
            raise

    def _create_control_table(self):
        """Esta tabla la agregué para controlar los jobs.
        
        Al principio no la tenía, pero me di cuenta que necesitaba
        saber qué jobs se habían ejecutado y cuáles habían fallado.
        """
        control_table = Table(
            'etl_control',
            self.metadata,
            Column('job_name', String, primary_key=True),
            Column('last_run_date', DateTime),
            Column('status', String),
            Column('records_processed', String),
            Column('error_message', String)
        )
        self.metadata.create_all(self.engine)

    def _execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Esta función es la que hace el trabajo pesado.
        
        Le agregué reintentos porque a veces la base de datos
        se pone un poco lenta y falla la primera vez.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as conn:
                    result = pd.read_sql(query, conn, params=params)
                    return result
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"¡No pude ejecutar la query después de {max_retries} intentos! Error: {e}")
                    raise
                logger.warning(f"Intento {attempt + 1} falló, voy a intentar de nuevo...")

    def get_daily_transactions(self, product: str, date: Optional[str] = None) -> Dict:
        """Este método me quedó genial.
        
        La caché la agregué después porque vi que las mismas consultas
        se hacían muchas veces. Ahora es mucho más rápido.
        """
        job_name = f"daily_transactions_{product}_{date if date else 'all'}"
        cache_key = f"transactions_{product}_{date}"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Primero vemos si ya procesamos esto hoy
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT status, records_processed
                        FROM etl_control
                        WHERE job_name = :job_name
                        AND DATE(last_run_date) = CURRENT_DATE
                    """),
                    {"job_name": job_name}
                ).fetchone()

                if result and result[0] == 'success':
                    logger.info(f"¡Encontré datos en caché para {job_name}!")
                    return {"cached": True, "data": result[1]}

            # Esta query la optimicé varias veces
            query = """
                SELECT 
                    c.nombre || ' ' || c.apellido as cliente,
                    COUNT(v.id) as cantidad_transacciones,
                    SUM(v.monto) as monto_total
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                WHERE v.producto = :product
            """
            params = {"product": product}
            
            if date:
                query += " AND v.fecha = :date"
                params["date"] = date
            
            query += " GROUP BY c.id, c.nombre, c.apellido"
            
            result = self._execute_query(query, params)
            
            data = {
                "producto": product,
                "fecha": date,
                "transacciones": result.to_dict(orient="records")
            }

            # Guardamos el éxito
            self._update_control(
                job_name,
                "success",
                str(len(result))
            )
            
            if self.cache is not None:
                self.cache[cache_key] = data
            
            return data
        except Exception as e:
            error_msg = str(e)
            self._update_control(job_name, "error", error=error_msg)
            logger.error(f"¡Error al obtener transacciones diarias! Detalles: {error_msg}")
            raise

    def get_top_clients(self, limit: int = 5) -> List[Dict]:
        """Este método es para ver quiénes son los mejores clientes.
        
        El límite lo hice configurable porque a veces queremos ver
        más o menos clientes del top.
        """
        job_name = f"top_clients_{limit}"
        cache_key = f"top_clients_{limit}"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Verificamos la caché del día
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT status, records_processed
                        FROM etl_control
                        WHERE job_name = :job_name
                        AND DATE(last_run_date) = CURRENT_DATE
                    """),
                    {"job_name": job_name}
                ).fetchone()

                if result and result[0] == 'success':
                    logger.info(f"¡Datos en caché para {job_name}!")
                    return {"cached": True, "data": result[1]}

            # Esta query está bien optimizada
            query = """
                SELECT 
                    c.nombre || ' ' || c.apellido as cliente,
                    SUM(v.monto) as monto_total
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                WHERE v.fecha >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY c.id, c.nombre, c.apellido
                ORDER BY monto_total DESC
                LIMIT :limit
            """
            
            result = self._execute_query(query, {"limit": limit})
            
            data = result.to_dict(orient="records")

            # Registramos el éxito
            self._update_control(
                job_name,
                "success",
                str(len(result))
            )
            
            if self.cache is not None:
                self.cache[cache_key] = data
            
            return data
        except Exception as e:
            error_msg = str(e)
            self._update_control(job_name, "error", error=error_msg)
            logger.error(f"¡Problemas al obtener top clientes! Error: {error_msg}")
            raise

    def get_average_ticket(self) -> Dict:
        """Este método calcula el ticket promedio.
        
        Al principio solo calculaba el promedio simple,
        pero después agregué el conteo de transacciones
        para tener más información.
        """
        job_name = "average_ticket"
        cache_key = "average_ticket"
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Revisamos la caché del día
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT status, records_processed
                        FROM etl_control
                        WHERE job_name = :job_name
                        AND DATE(last_run_date) = CURRENT_DATE
                    """),
                    {"job_name": job_name}
                ).fetchone()

                if result and result[0] == 'success':
                    logger.info(f"¡Encontré datos en caché para {job_name}!")
                    return {"cached": True, "data": result[1]}

            # Esta query es simple pero efectiva
            query = """
                SELECT 
                    AVG(v.monto) as ticket_promedio,
                    COUNT(v.id) as total_transacciones
                FROM ventas v
                WHERE v.fecha >= CURRENT_DATE - INTERVAL '1 year'
            """
            
            result = self._execute_query(query)
            
            data = {
                "ticket_promedio": float(result["ticket_promedio"].iloc[0]),
                "total_transacciones": int(result["total_transacciones"].iloc[0])
            }

            # Guardamos el éxito
            self._update_control(
                job_name,
                "success",
                str(result["total_transacciones"].iloc[0])
            )
            
            if self.cache is not None:
                self.cache[cache_key] = data
            
            return data
        except Exception as e:
            error_msg = str(e)
            self._update_control(job_name, "error", error=error_msg)
            logger.error(f"¡Error al calcular ticket promedio! Detalles: {error_msg}")
            raise

    def _update_control(self, job_name: str, status: str, records: str = None, error: str = None):
        """Esta función actualiza el control de jobs.
        
        El ON CONFLICT fue clave para que fuera idempotente.
        Me costó un poco pero al final quedó bien.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO etl_control (job_name, last_run_date, status, records_processed, error_message)
                        VALUES (:job_name, :date, :status, :records, :error)
                        ON CONFLICT (job_name) DO UPDATE
                        SET last_run_date = :date,
                            status = :status,
                            records_processed = :records,
                            error_message = :error
                    """),
                    {
                        "job_name": job_name,
                        "date": datetime.now(),
                        "status": status,
                        "records": records,
                        "error": error
                    }
                )
                conn.commit()
        except Exception as e:
            logger.error(f"¡Error al actualizar el control ETL! Detalles: {str(e)}")
            raise 