# Arquitectura del Sistema

## Visión General
El sistema está compuesto por dos pipelines principales que trabajan en conjunto para proporcionar análisis de ventas tanto históricos como en tiempo real.

## Pipeline Batch
[![Pipeline Batch](diagrams/batch_pipeline.drawio)](diagrams/batch_pipeline.drawio)

### Descripción
Pipeline diseñado para procesar datos históricos diariamente, generando reportes consolidados para cada proveedor.

### Componentes Clave
- **Origen**: Amazon RDS
- **Procesamiento**: 
  - AWS Glue (glue_job.py)
  - Procesador Diario (daily_processor.py)
- **Almacenamiento**: Amazon S3
- **Exposición**: API Gateway

### Flujo de Datos
1. Extracción diaria de datos de RDS
2. Procesamiento con AWS Glue
3. Almacenamiento en S3 particionado
4. Exposición a través de API

## Pipeline Tiempo Real
[![Pipeline Tiempo Real](diagrams/realtime_pipeline.drawio)](diagrams/realtime_pipeline.drawio)

### Descripción
Pipeline diseñado para procesar transacciones en tiempo real y mantener métricas actualizadas.

### Componentes Clave
- **Origen**: Amazon RDS
- **Procesamiento**: 
  - Stream Processor (stream_processor.py)
  - Kinesis Analytics (kinesis_analytics_app.sql)
- **Almacenamiento**: DynamoDB
- **Exposición**: API Gateway

### Flujo de Datos
1. Extracción continua de RDS
2. Procesamiento con Kinesis Analytics
3. Almacenamiento en DynamoDB
4. Exposición a través de API

## Integración
Los pipelines se complementan para ofrecer:
1. Análisis histórico detallado (Batch)
2. Métricas en tiempo real (Realtime)
3. API unificada para consultas

## Consideraciones de Seguridad

1. **Acceso a Datos**
   - IAM roles específicos
   - Least privilege principle

2. **Encriptación**
   - En tránsito (TLS)
   - En reposo (KMS)

3. **Monitoreo**
   - CloudWatch Logs
   - Métricas de rendimiento

## Escalabilidad

1. **Pipeline Batch**
   - Glue workers auto-scaling
   - S3 particionamiento

2. **Pipeline Tiempo Real**
   - Kinesis Analytics auto-scaling
   - DynamoDB auto-scaling

## Costos

1. **Optimizaciones**
   - S3 lifecycle policies
   - Auto-scaling policies

2. **Monitoreo**
   - Cost Explorer
   - Budgets

## Arquitectura de Calidad y Rendimiento

### Sistema de Testing
La arquitectura de pruebas está diseñada en tres capas:

1. **Capa de API**
   - Tests de integración para endpoints
   - Validación de flujos completos
   - Simulación de escenarios de error
   - Verificación de seguridad

2. **Capa de Servicio**
   - Tests unitarios de lógica de negocio
   - Verificación de interacción con bases de datos
   - Pruebas de manejo de errores
   - Validación de caché

3. **Capa de Procesamiento**
   - Tests de precisión de cálculos
   - Validación de transformaciones de datos
   - Pruebas de rendimiento
   - Verificación de casos límite

### Sistema de Monitoreo
Arquitectura basada en AWS CloudWatch:

1. **Recolección de Métricas**
   ```
   Aplicación -> CloudWatch -> Dashboards
        |
        └-> Logs -> Alertas
   ```

2. **Tipos de Métricas**
   - Métricas de Negocio
     * Transacciones procesadas
     * Tasa de éxito
     * Volumen de datos
   - Métricas Técnicas
     * Latencia de API
     * Uso de recursos
     * Errores del sistema

3. **Sistema de Alertas**
   - Umbrales configurables
   - Notificaciones por SNS
   - Escalamiento automático de incidentes

### Sistema de Caché
Arquitectura de caché en múltiples niveles:

1. **Nivel de Aplicación**
   ```
   Cliente -> API -> Caché -> Base de Datos
   ```

2. **Estrategias de Caché**
   - Caché de resultados frecuentes
   - Invalidación por tiempo
   - Actualización proactiva
   - Gestión de concurrencia

3. **Monitoreo de Caché**
   - Tasa de aciertos/fallos
   - Uso de memoria
   - Tiempo de respuesta
   - Patrones de acceso

### Integración de Componentes

La integración de estos sistemas proporciona:

1. **Calidad**
   - Detección temprana de problemas
   - Mantenimiento proactivo
   - Mejora continua

2. **Rendimiento**
   - Optimización automática
   - Escalabilidad
   - Eficiencia en recursos

3. **Operación**
   - Visibilidad completa
   - Respuesta rápida a incidentes
   - Mejora continua 