# Respuestas Prácticas - Prueba Técnica Puntored

## SQL

### 1. Top 5 clientes con mayor monto en últimos 6 meses
```sql
SELECT 
    c.id,
    c.nombre,
    c.apellido,
    SUM(v.monto) as monto_total
FROM 
    clientes c
JOIN 
    ventas v ON c.id = v.cliente_id
WHERE 
    v.fecha >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY 
    c.id, c.nombre, c.apellido
ORDER BY 
    monto_total DESC
LIMIT 5;
```

### 2. Ticket promedio por cliente en último año
```sql
SELECT 
    c.id,
    c.nombre,
    c.apellido,
    AVG(v.monto) as ticket_promedio
FROM 
    clientes c
JOIN 
    ventas v ON c.id = v.cliente_id
WHERE 
    v.fecha >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY 
    c.id, c.nombre, c.apellido;
```

### 3. Nombre completo y monto total de ventas
```sql
SELECT 
    c.nombre || ' ' || c.apellido as nombre_completo,
    SUM(v.monto) as monto_total
FROM 
    clientes c
JOIN 
    ventas v ON c.id = v.cliente_id
GROUP BY 
    c.id, c.nombre, c.apellido;
```

### 4. Ingreso promedio por mes
```sql
SELECT 
    DATE_TRUNC('month', v.fecha) as mes,
    AVG(v.monto) as ingreso_promedio
FROM 
    ventas v
GROUP BY 
    mes
ORDER BY 
    mes;
```

### 5. Ranking de clientes por ventas en último año
```sql
SELECT 
    c.nombre || ' ' || c.apellido as nombre_completo,
    SUM(v.monto) as monto_total,
    RANK() OVER (ORDER BY SUM(v.monto) DESC) as ranking
FROM 
    clientes c
JOIN 
    ventas v ON c.id = v.cliente_id
WHERE 
    v.fecha >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY 
    c.id, c.nombre, c.apellido;
```

### 6. Clientes con ventas superiores al promedio
```sql
WITH promedio_ventas AS (
    SELECT AVG(monto) as promedio
    FROM ventas
)
SELECT 
    c.nombre || ' ' || c.apellido as nombre_completo,
    SUM(v.monto) as monto_total
FROM 
    clientes c
JOIN 
    ventas v ON c.id = v.cliente_id
GROUP BY 
    c.id, c.nombre, c.apellido
HAVING 
    SUM(v.monto) > (SELECT promedio FROM promedio_ventas);
```

## Python y AWS

### 1. Pipeline Batch
El pipeline batch implementado utiliza:
- **AWS Glue**: Para la extracción y transformación de datos
  - Job implementado en `src/batch/glue_job.py`
  - Utiliza PySpark para procesamiento eficiente
  - Particionamiento por fecha y producto
- **Amazon S3**: Para almacenamiento de datos procesados
  - Estructura: `s3://puntored-analytics/processed/{producto}/{fecha}/`
  - Formato Parquet para mejor rendimiento
- **AWS Lambda**: Para procesamiento por proveedor
- **Amazon API Gateway**: Para exposición de la API

Flujo implementado:
1. Glue Crawler cataloga las tablas en RDS
2. Glue ETL procesa datos diariamente
3. Resultados se guardan en S3 en formato Parquet
4. API expone datos procesados

### 2. Pipeline Tiempo Real
El pipeline en tiempo real implementado utiliza:
- **Amazon Kinesis**: Para captura de datos en tiempo real
  - Handler implementado en `src/realtime/kinesis_handler.py`
  - Procesamiento por lotes de registros
  - Manejo de errores y reintentos
- **AWS Lambda**: Para procesamiento stream
  - Función Lambda integrada con Kinesis
  - Actualización en tiempo real de métricas
- **Amazon DynamoDB**: Para almacenamiento rápido
  - Tabla con partición por cliente y fecha
  - Actualización atómica de contadores
- **Amazon API Gateway**: Para exposición de la API
  - Endpoints REST con autenticación
  - Caché de respuestas

Flujo implementado:
1. Kinesis captura transacciones en tiempo real
2. Lambda procesa cada registro
3. DynamoDB mantiene contadores actualizados
4. API Gateway expone datos en tiempo real

### 3. Script de Extracción
Implementado en `src/services/data_service.py`:
- Conexión a RDS usando SQLAlchemy
- Consultas optimizadas por producto
- Sistema de caché para mejorar rendimiento
- Manejo de errores y logging detallado
- Control de jobs y reintentos

### 4. API REST
Implementado en `src/api/main.py`:
- FastAPI para endpoints REST
- Autenticación con API Key
- CORS configurado para seguridad
- Documentación automática con Swagger
- Manejo de errores y validaciones
- Logs detallados de cada operación
- Caché de respuestas frecuentes

Endpoints implementados:
- `/health`: Verificación de estado
- `/transacciones`: Datos por producto y fecha
- `/top-clientes`: Ranking de clientes
- `/ticket-promedio`: Análisis de ventas

Seguridad:
- API Key requerida en header `X-API-Key`
- CORS limitado a orígenes permitidos
- Validación de parámetros de entrada
- Manejo de errores HTTP estándar 
