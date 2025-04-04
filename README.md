# Prueba Técnica - Data Engineer PuntoRed

Este repositorio contiene mi solución a la prueba técnica. Implementé un sistema que permite a tres proveedores consultar sus datos de ventas a través de una API, incluyendo tanto análisis histórico como datos en tiempo real.

## Respuestas a la Prueba

Organicé las respuestas según las secciones del documento:

- **Sección 1** - [Preguntas teóricas](respuestas/respuestas_teoricas.md) sobre Python, SQL y AWS
- **Sección 2** - [Consultas SQL](respuestas/respuestas_practicas.md) para análisis de ventas
- **Sección 3** - Implementación práctica (este repositorio)

## El Proyecto

El código está principalmente en Python usando FastAPI para la API REST y servicios de AWS para el procesamiento de datos. Toda la documentación técnica está en la carpeta `docs/`:
- [Arquitectura](docs/arquitectura.md) - Cómo está diseñado el sistema
- [Pipelines](docs/pipelines.md) - Detalles de implementación
- [API](docs/api.md) - Guía de uso de endpoints
- [Diagramas](docs/diagrams/) - Visuales del sistema

Estructura completa del proyecto:
```
DEPuntoRED/
├── src/
│   ├── api/           # API REST con FastAPI
│   ├── batch/        # Pipeline de procesamiento diario
│   ├── realtime/     # Pipeline en tiempo real
│   ├── services/     # Servicios compartidos
│   ├── utils/        # Utilidades generales
│   ├── config/       # Configuraciones
│   └── database/     # Modelos y conexiones DB
│
├── tests/           # Tests automatizados
├── docs/           # Documentación técnica
│   ├── arquitectura.md
│   ├── pipelines.md
│   ├── api.md
│   └── diagrams/
├── respuestas/     # Respuestas a la prueba
│   ├── respuestas_teoricas.md
│   └── respuestas_practicas.md
├── data/          # Datos de ejemplo
├── config/        # Configuraciones globales
│
├── .env           # Variables de entorno
├── requirements.txt # Dependencias Python
├── .gitignore    # Archivos ignorados
└── README.md     # Este archivo
```

### Lo que Construí

**Pipeline Batch**
- Procesamiento diario con AWS Glue
- Almacenamiento en S3
- Reportes por proveedor

**Pipeline Tiempo Real**
- Ingesta con Kinesis
- DynamoDB para consultas rápidas
- Métricas en tiempo real

**API REST**
- Endpoints específicos por proveedor
- Autenticación con API Key
- Documentación interactiva en `/docs`

## Para Empezar a Desarrollar

Vas a necesitar:
- Python 3.8+
- PostgreSQL 13+
- AWS CLI configurado

Pasos básicos:
```bash
# Clonar y configurar
git clone https://github.com/usuario/DEPuntoRed.git
cd DEPuntoRed
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar env
cp .env.example .env
# Editar .env con tus credenciales

# Correr API
uvicorn src.api.main:app --reload
```

## Preguntas Rápidas

### Windows o Linux?
Linux en producción por estabilidad. Windows en desarrollo por comodidad local.

### MySQL o PostgreSQL?
PostgreSQL. Necesitaba sus capacidades analíticas y mejor rendimiento con grandes volúmenes de datos.

### Batch o Streaming?
Ambos. Batch para análisis históricos profundos, streaming para datos en tiempo real.

### ETL o ELT?
ELT. Aprovechando al máximo las capacidades de procesamiento en la nube.

### Parquet o CSV?
Parquet. Mejor compresión y rendimiento en consultas analíticas.

### Spark o Pandas?
Pandas por ahora. La escala actual no justifica Spark, pero está considerado para cuando crezca.



## Solución Alternativa: Databricks

Como alternativa, implementé la solución usando Databricks, que ofrece:
- Procesamiento unificado
- Escalabilidad automática
- Gestión simplificada

### Solución en Databricks

La solución en Databricks está diseñada para cumplir con los requerimientos específicos de la prueba técnica, enfocándose en:
- Procesamiento diario de ventas por proveedor
- Disponibilidad de datos en tiempo real
- Formato JSON para la API

#### Estructura de Notebooks
```
notebooks/
├── batch/
│   ├── 01_extract_daily_data.json     # Extracción y procesamiento diario
│   ├── 02_transform_sales.json        # Transformación y enriquecimiento
│   └── 03_load_analytics.json         # Preparación para API
├── streaming/
│   ├── 01_ingest_stream.json          # Ingesta desde Kafka
│   └── 02_process_realtime.json       # Procesamiento en tiempo real
└── utils/
    ├── common_functions.json          # Funciones compartidas
    └── config.json                    # Configuración global
```

#### Pipeline Batch
1. **Extracción y Procesamiento (01_extract_daily_data)**
   - Lectura de datos del día anterior
   - Cálculo de métricas por proveedor:
     ```python
     - cantidad_transacciones
     - monto_total
     ```
   - Formato JSON para la API
   - Almacenamiento en S3

2. **Transformación (02_transform_sales)**
   - Enriquecimiento de datos
   - Validación de registros
   - Preparación para análisis

3. **Carga (03_load_analytics)**
   - Optimización de datos
   - Preparación para la API
   - Validación final

#### Pipeline Streaming
1. **Ingesta (01_ingest_stream)**
   - Conexión con Kafka
   - Validación de eventos
   - Preparación de datos

2. **Procesamiento en Tiempo Real (02_process_realtime)**
   - Extracción de datos recientes
   - Envío a Kinesis para procesamiento
   - Alertas para transacciones grandes
   - Monitoreo con CloudWatch

#### Características Técnicas

1. **Procesamiento Simple y Eficiente**
   - Consultas SQL directas a RDS
   - Formato JSON para la API
   - Sin transformaciones complejas

2. **Monitoreo Básico**
   - Logging de operaciones
   - Alertas para transacciones grandes
   - Métricas en CloudWatch

3. **Configuración Mínima**
   ```python
   Configuración básica:
   - Conexión a RDS
   - Bucket S3 para resultados
   - Stream de Kinesis
   ```

## Autor
Erick Sang 