import redis
import json
from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
from src.config.settings import CACHE_CONFIG
from src.utils.monitoring import logger

class Cache:
    """Clase para manejar el caché usando Redis"""
    
    def __init__(self):
        """Inicializa la conexión con Redis"""
        self.redis_client = redis.Redis(
            host=CACHE_CONFIG['host'],
            port=CACHE_CONFIG['port'],
            db=CACHE_CONFIG['db'],
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Error al obtener del caché: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, expiration: int = 3600) -> bool:
        """Guarda un valor en el caché"""
        try:
            self.redis_client.setex(
                key,
                expiration,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Error al guardar en caché: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina un valor del caché"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error al eliminar del caché: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Limpia todo el caché"""
        try:
            return bool(self.redis_client.flushdb())
        except Exception as e:
            logger.error(f"Error al limpiar el caché: {str(e)}")
            return False

# Instancia global del caché
cache = Cache()

def cached(expiration: int = 3600):
    """Decorador para cachear resultados de funciones"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Genera una clave única basada en la función y sus argumentos
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Intenta obtener el resultado del caché
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit para {func.__name__}")
                return cached_result
            
            # Si no está en caché, ejecuta la función
            result = func(*args, **kwargs)
            
            # Guarda el resultado en caché
            cache.set(cache_key, result, expiration)
            logger.info(f"Cache miss para {func.__name__}, resultado guardado")
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str) -> None:
    """Invalida todas las claves que coincidan con un patrón"""
    try:
        keys = cache.redis_client.keys(pattern)
        if keys:
            cache.redis_client.delete(*keys)
            logger.info(f"Caché invalidado para el patrón: {pattern}")
    except Exception as e:
        logger.error(f"Error al invalidar caché: {str(e)}")

def get_cache_stats() -> dict:
    """Obtiene estadísticas del uso del caché"""
    try:
        info = cache.redis_client.info()
        return {
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'memory_used': info.get('used_memory_human', '0B'),
            'total_keys': cache.redis_client.dbsize()
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del caché: {str(e)}")
        return {} 