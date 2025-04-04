import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from datetime import datetime, timedelta

# Inicialización del job
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configuraciones
database = "ventas_db"
table_ventas = "ventas"
s3_output_path = "s3://puntored-analytics/batch/"
fecha_proceso = datetime.now().strftime("%Y-%m-%d")

try:
    # Leer datos de ventas del día anterior
    ventas_df = glueContext.create_dynamic_frame.from_catalog(
        database=database,
        table_name=table_ventas,
        push_down_predicate="fecha >= date_sub(current_date, 1)"
    ).toDF()
    
    # Procesar datos para cada proveedor
    productos = ["PRODUCTO_1", "PRODUCTO_2", "PRODUCTO_3"]
    
    for producto in productos:
        # Filtrar por producto (proveedor)
        df_proveedor = ventas_df.filter(F.col("producto") == producto)
        
        # Calcular métricas requeridas por proveedor
        metricas_df = df_proveedor.groupBy(
            "cliente_id",
            F.to_date("fecha").alias("fecha")
        ).agg(
            F.count("*").alias("cantidad_transacciones"),
            F.sum("monto").alias("monto_total")
        )
        
        # Preparar datos en formato requerido
        resultado_df = metricas_df.select(
            F.col("cliente_id"),
            F.col("fecha"),
            F.col("cantidad_transacciones"),
            F.round("monto_total", 2).alias("monto_total")
        )
        
        # Escribir resultados particionados por fecha
        output_path = f"{s3_output_path}proveedor_{producto}/fecha={fecha_proceso}/"
        
        resultado_df.write \
            .mode("overwrite") \
            .format("json") \
            .save(output_path)
        
        print(f"Procesamiento completado para {producto}")

except Exception as e:
    print(f"Error en el job: {str(e)}")
    raise
finally:
    job.commit() 