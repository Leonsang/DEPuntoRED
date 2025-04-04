# Documentación Técnica - PuntoRed Analytics

## Índice

### 1. [Arquitectura General](arquitectura.md)
- Visión general del sistema
- Componentes principales
- Flujos de datos

### 2. [Pipelines de Datos](pipelines.md)
- [Pipeline Batch](pipelines.md#pipeline-batch)
  - Configuración de AWS Glue
  - Estructura de S3
  - Formato de datos
- [Pipeline Tiempo Real](pipelines.md#pipeline-tiempo-real)
  - Configuración de Kinesis Analytics
  - Procesamiento en tiempo real
  - Monitoreo y alertas

### 3. [API REST](api.md)
- [Endpoints](api.md#endpoints)
  - Métricas por Cliente
  - Métricas por Producto
- [Seguridad](api.md#seguridad)
- [Rendimiento](api.md#rendimiento)

### 4. [Diagramas](diagrams/)
- [Pipeline Batch](diagrams/batch_pipeline.drawio)
- [Pipeline Tiempo Real](diagrams/realtime_pipeline.drawio)

## Estructura del Proyecto

```
DEPuntoRed/
├── src/
│   ├── api/           # API REST con FastAPI
│   │   ├── main.py    # Endpoints principales
│   │   └── app.py     # Configuración de la aplicación
│   │
│   ├── batch/         # Pipeline de procesamiento diario
│   │   ├── glue_job.py        # Job de AWS Glue
│   │   └── daily_processor.py # Procesador diario
│   │
│   ├── realtime/      # Pipeline en tiempo real
│   │   ├── stream_processor.py        # Procesador de streams
│   │   └── kinesis_analytics_app.sql  # SQL para Kinesis Analytics
│   │
│   ├── services/      # Servicios compartidos
│   │   └── data_service.py    # Servicio de datos
│   │
│   ├── utils/         # Utilidades generales
│   │   ├── cache.py          # Manejo de caché
│   │   └── monitoring.py     # Monitoreo y métricas
│   │
│   ├── config/        # Configuraciones
│   │   └── settings.py       # Configuración global
│   │
│   └── database/      # Modelos y conexiones DB
│       ├── models.py         # Modelos de datos
│       └── setup.py          # Configuración de la base de datos
│
├── docs/             # Documentación técnica
│   ├── arquitectura.md
│   ├── pipelines.md
│   ├── api.md
│   └── diagrams/
│
└── README.md         # Documentación principal
```

## Componentes Principales

### Pipeline Batch
- Procesamiento diario con AWS Glue
- Almacenamiento en S3
- Reportes por proveedor

### Pipeline Tiempo Real
- Ingesta con Kinesis Analytics
- Procesamiento en tiempo real
- Métricas y alertas

### API REST
- Endpoints específicos por proveedor
- Autenticación con API Key
- Documentación en formato JSON

### Servicios Compartidos
- Funcionalidades comunes
- Utilidades de procesamiento
- Manejo de configuraciones

### Base de Datos
- Modelos de datos
- Conexiones y queries
- Configuración de RDS

## Requisitos Técnicos

- Python 3.8+
- PostgreSQL 13+
- AWS CLI configurado
- Acceso a servicios AWS:
  - Glue
  - Kinesis Analytics
  - S3
  - DynamoDB

## Contacto
Para soporte técnico o preguntas, contactar al equipo de desarrollo. 