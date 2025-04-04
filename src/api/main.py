# API principal para el análisis de ventas
# TODO: Agregar autenticación y validaciones

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import logging
from datetime import datetime

from ..services.data_service import DataService
from ..config.settings import API_CONFIG, LOG_CONFIG

# Configuración básica de logs
logging.basicConfig(
    level=LOG_CONFIG["level"],
    format=LOG_CONFIG["format"]
)
logger = logging.getLogger(__name__)

# Configuración de API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Valida la API key proporcionada"""
    if api_key_header == API_CONFIG["api_key"]:
        return api_key_header
    raise HTTPException(
        status_code=403,
        detail="Could not validate API Key"
    )

# Inicialización de FastAPI
app = FastAPI(
    title="PuntoRed Analytics API",
    description="""
    API para análisis de ventas de PuntoRed.
    
    Permite a los proveedores consultar:
    * Transacciones diarias por producto
    * Top clientes por volumen de ventas
    * Ticket promedio de ventas
    
    Toda petición requiere autenticación mediante API Key en el header 'X-API-Key'.
    """,
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo PuntoRed",
        "email": "dev@puntored.com"
    }
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG["allowed_origins"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Servicio de datos
data_service = DataService()

def _format_response(data: any, message: str = "OK") -> Dict:
    """Formatea la respuesta de la API"""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Monitoreo"])
async def health_check():
    """
    Verifica que la API esté funcionando correctamente.
    
    Returns:
        dict: Estado de salud de la API
    """
    try:
        data_service.get_average_ticket()
        return _format_response({"status": "healthy"})
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.get("/transacciones", tags=["Consultas"])
async def get_transacciones(
    producto: str,
    fecha: str = None,
    api_key: APIKey = Depends(get_api_key)
):
    """
    Obtiene las transacciones por producto y fecha.
    
    Args:
        producto: Identificador del producto
        fecha: Fecha en formato YYYY-MM-DD (opcional, default: fecha actual)
        
    Returns:
        dict: Lista de transacciones con sus detalles
        
    Raises:
        400: Parámetros inválidos
        403: API Key inválida
        500: Error interno del servidor
    """
    try:
        data = data_service.get_daily_transactions(producto, fecha)
        return _format_response(data)
    except ValueError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en transacciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-clientes", tags=["Consultas"])
async def get_top_clientes(
    limit: int = 5,
    api_key: APIKey = Depends(get_api_key)
):
    """
    Obtiene los mejores clientes por monto de ventas.
    
    Args:
        limit: Número de clientes a retornar (1-100, default: 5)
        
    Returns:
        dict: Lista de clientes con sus montos totales
        
    Raises:
        400: Límite fuera de rango
        403: API Key inválida
        500: Error interno del servidor
    """
    try:
        if limit < 1 or limit > 100:
            raise ValueError("El límite debe estar entre 1 y 100")
        data = data_service.get_top_clients(limit)
        return _format_response(data)
    except ValueError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en top clientes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticket-promedio", tags=["Consultas"])
async def get_ticket_promedio(api_key: APIKey = Depends(get_api_key)):
    """
    Calcula el ticket promedio de ventas.
    
    Returns:
        dict: Ticket promedio y métricas relacionadas
        
    Raises:
        403: API Key inválida
        500: Error interno del servidor
    """
    try:
        data = data_service.get_average_ticket()
        return _format_response(data)
    except Exception as e:
        logger.error(f"Error en ticket promedio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        reload=API_CONFIG["debug"]
    ) 