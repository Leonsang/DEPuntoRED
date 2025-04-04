# Acá van todas las configuraciones del proyecto
# No me gusta tener cosas hardcodeadas, así que todo va en variables de entorno

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargamos las variables de entorno
# Ojo con el .env, no lo subas a git!
load_dotenv()

# Definimos las rutas principales
# Esto es útil para no andar escribiendo rutas a mano
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Creamos los directorios si no existen
# Mejor prevenir que lamentar
for dir_path in [DATA_DIR, LOGS_DIR, CONFIG_DIR]:
    dir_path.mkdir(exist_ok=True)

# Configuración básica del proyecto
# TODO: Mover a variables de entorno en producción

# Base de datos
DB_CONFIG = {
    "url": "postgresql://user:password@localhost:5432/puntored",
    "pool_size": 5,
    "max_overflow": 10,
    "echo": False
}

# API
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True
}

# Logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Caché
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600  # 1 hora
}

# Configuración de almacenamiento
# S3 es caro, mejor guardamos local por ahora
STORAGE_CONFIG = {
    "path": os.getenv("STORAGE_PATH", str(DATA_DIR)),
    "retention_days": int(os.getenv("STORAGE_RETENTION_DAYS", "30")),
    "compression": os.getenv("STORAGE_COMPRESSION", "True").lower() == "true"
}

# Configuración de procesamiento
# Esto es para no saturar la base de datos
PROCESSING_CONFIG = {
    "batch_size": int(os.getenv("PROCESSING_BATCH_SIZE", "1000")),
    "max_retries": int(os.getenv("PROCESSING_MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("PROCESSING_RETRY_DELAY", "5")),
    "timeout": int(os.getenv("PROCESSING_TIMEOUT", "300"))
}

# Configuración de productos
# Acá definimos qué productos vamos a procesar
PRODUCTS_CONFIG = {
    "enabled": os.getenv("ENABLED_PRODUCTS", "product1,product2,product3").split(","),
    "default_currency": os.getenv("DEFAULT_CURRENCY", "USD"),
    "decimal_places": int(os.getenv("DECIMAL_PLACES", "2"))
}

# Configuración de seguridad
# Esto es importante, no lo descuides
SECURITY_CONFIG = {
    "api_key": os.getenv("API_KEY", "changeme"),
    "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
    "rate_limit": int(os.getenv("RATE_LIMIT", "100")),
    "timeout": int(os.getenv("SECURITY_TIMEOUT", "30"))
}

# Configuración de monitoreo
# Para saber qué está pasando con la aplicación
MONITORING_CONFIG = {
    "enabled": os.getenv("MONITORING_ENABLED", "True").lower() == "true",
    "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
    "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
} 