# Databricks notebook source
# MAGIC %md
# MAGIC # Ingesta de Datos en Tiempo Real
# MAGIC Procesa eventos de ventas desde Kafka y los almacena en Delta Lake

# COMMAND ----------
# MAGIC %run "../utils/config"

# COMMAND ----------
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Schema para los eventos de ventas
schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("provider_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("client_id", StringType(), True),
    StructField("timestamp", TimestampType(), True)
])

# COMMAND ----------
# Configuración del stream
stream_config = get_stream_config()

# Leer stream de Kafka
df_stream = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", stream_config["kafka_bootstrap_servers"])
    .option("subscribe", stream_config["kafka_topic"])
    .load()
)

# Parsear JSON y aplicar schema
df_parsed = df_stream.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# COMMAND ----------
# Escribir a Delta Lake
query = (df_parsed.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", stream_config["checkpoint_location"])
    .trigger(processingTime=stream_config["trigger_interval"])
    .toTable("raw_sales")
)

# COMMAND ----------
# Métricas en tiempo real
df_metrics = (df_parsed
    .withWatermark("timestamp", "1 minute")
    .groupBy(
        window("timestamp", "1 minute"),
        "provider_id",
        "product_id"
    )
    .agg(
        count("*").alias("transaction_count"),
        sum("amount").alias("total_amount"),
        avg("amount").alias("avg_amount")
    )
)

# COMMAND ----------
# Escribir métricas
query_metrics = (df_metrics.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", f"{stream_config['checkpoint_location']}/metrics")
    .trigger(processingTime=stream_config["trigger_interval"])
    .toTable("realtime_metrics")
) 