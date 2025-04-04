# Databricks notebook source
# MAGIC %md
# MAGIC # Configuración Global para Notebooks
# MAGIC Configuraciones compartidas entre los notebooks de batch y streaming

# COMMAND ----------
# Configuración de datos
DATABASE_NAME = "puntored_analytics"
DELTA_PATH = "/delta/puntored"

# Configuración de tablas
TABLES = {
    "raw_sales": f"{DELTA_PATH}/raw_sales",
    "daily_metrics": f"{DELTA_PATH}/daily_metrics",
    "realtime_metrics": f"{DELTA_PATH}/realtime_metrics",
    "top_clients": f"{DELTA_PATH}/top_clients"
}

# Configuración de streaming
STREAM_CONFIG = {
    "kafka_bootstrap_servers": "kafka:9092",
    "kafka_topic": "sales_events",
    "trigger_interval": "1 minute",
    "checkpoint_location": f"{DELTA_PATH}/checkpoints"
}

# Configuración de procesamiento batch
BATCH_CONFIG = {
    "source_format": "json",
    "write_mode": "merge",
    "partition_columns": ["date", "provider_id"],
    "vacuum_retention": "7 days"
}

# COMMAND ----------
# Funciones de utilidad para configuración

def init_database():
    """Inicializa la base de datos si no existe"""
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    spark.sql(f"USE {DATABASE_NAME}")

def get_delta_path(table_name):
    """Obtiene la ruta Delta para una tabla"""
    return TABLES.get(table_name)

def get_stream_config():
    """Obtiene la configuración de streaming"""
    return STREAM_CONFIG

def get_batch_config():
    """Obtiene la configuración de procesamiento batch"""
    return BATCH_CONFIG

# COMMAND ----------
# Inicialización
init_database() 