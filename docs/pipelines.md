# Pipelines de Datos

## Tabla de Contenidos
- [Pipeline Batch](#pipeline-batch)
  - [Configuración de Componentes](#configuración-de-componentes)
  - [Formato de Datos](#formato-de-datos)
- [Pipeline Tiempo Real](#pipeline-tiempo-real)
  - [Configuración de Componentes](#configuración-de-componentes-1)
  - [Formato de Datos](#formato-de-datos-1)
- [API REST](#api-rest)
  - [Endpoints](#endpoints)
  - [Seguridad y Rendimiento](#seguridad-y-rendimiento)

## Pipeline Batch

### Configuración de Componentes

1. **AWS Glue**
   - Job Type: Python Shell
   - Workers: 5 G.1X
   - Timeout: 30 minutos
   - Retry: 2 intentos
   - [Ver código del job](src/batch/glue_job.py)

2. **Amazon S3**
   ```
   s3://puntored-analytics/
   ├── batch/
   │   ├── proveedor_1/
   │   │   ├── year=2024/
   │   │   │   ├── month=03/
   │   │   │   │   └── day=21/
   │   ├── proveedor_2/
   │   └── proveedor_3/
   ```
   [Ver diagrama de estructura](diagrams/batch_pipeline.drawio)

3. **Formato de Datos**
   ```json
   {
     "cliente_id": "string",
     "nombre": "string",
     "apellido": "string",
     "fecha": "date",
     "transacciones": "integer",
     "monto_total": "decimal"
   }
   ```

## Pipeline Tiempo Real

### Configuración de Componentes

1. **Amazon RDS**
   - Motor: PostgreSQL
   - Tabla: ventas
   - Campos monitoreados:
     - cliente_id
     - producto
     - monto
     - fecha
   - [Ver esquema de base de datos](database/schema.md)

2. **Kinesis Analytics**
   - Input Stream: VENTAS_INPUT_STREAM
   - Output Stream: METRICAS_OUTPUT_STREAM
   - Ventana de agregación: 1 minuto
   - [Ver SQL de procesamiento](src/realtime/kinesis_analytics_app.sql)
   - [Ver diagrama de flujo](diagrams/realtime_pipeline.drawio)

3. **DynamoDB**
   ```
   Tabla: metricas_tiempo_real
   - PK: id (cliente_id#producto#fecha)
   - num_transacciones (number)
   - monto_total (number)
   - fecha_hora (timestamp)
   ```
   [Ver configuración de DynamoDB](aws/dynamodb.md)

4. **CloudWatch**
   - Métricas:
     - TransaccionesXMinuto
     - MontoTotalXMinuto
   - Alertas:
     - Transacciones > 1000/min
     - Monto individual > 1000
   - [Ver configuración de monitoreo](deployment.md#monitoreo)

### Formato de Datos

1. **Input (RDS → Kinesis)**
   ```json
   {
     "cliente_id": "integer",
     "producto": "string",
     "monto": "decimal",
     "fecha": "timestamp"
   }
   ```

2. **Output (DynamoDB)**
   ```json
   {
     "id": "string", // formato: "cliente_id#producto#YYYY-MM-DD"
     "num_transacciones": "integer",
     "monto_total": "decimal",
     "fecha_hora": "timestamp"
   }
   ```

## API REST

### Endpoints

1. **Métricas por Cliente**
   ```
   GET /metricas/cliente/{cliente_id}
   Query:
     - producto: string (optional)
     - fecha: string (optional, YYYY-MM-DD)
   Response:
     {
       "cliente_id": "integer",
       "metricas": {
         "num_transacciones": "integer",
         "monto_total": "decimal"
       }
     }
   ```
   [Ver implementación](src/api/main.py#L45)

2. **Métricas por Producto**
   ```
   GET /metricas/producto/{producto_id}
   Query:
     - fecha: string (optional, YYYY-MM-DD)
   Response:
     {
       "producto": "string",
       "metricas": {
         "num_transacciones": "integer",
         "monto_total": "decimal"
       }
     }
   ```
   [Ver implementación](src/api/main.py#L78)

### Seguridad y Rendimiento
- API Key requerida en header `X-API-Key`
- Rate limit: 1000 req/min
- Datos en tiempo real (latencia < 1 min)
- Monitoreo automático vía CloudWatch
- [Ver configuración de seguridad](api.md#seguridad)

---

[Volver al índice](README.md) 