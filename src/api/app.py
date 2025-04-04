from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import Dict, List
import boto3
from datetime import datetime
import os
import logging
from pydantic import BaseModel
import json
from boto3.dynamodb.conditions import Key

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de FastAPI
app = FastAPI(
    title="API de Métricas de Ventas",
    description="API para consulta de métricas de ventas por proveedor",
    version="1.0.0"
)

# Configuración de seguridad
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Modelos de datos
class MetricasResponse(BaseModel):
    cliente_id: str
    fecha: str
    num_transacciones: int
    monto_total: float

class ErrorResponse(BaseModel):
    error: str
    detail: str

# Configuración de AWS
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
elasticache_client = boto3.client('elasticache')

# Mapeo de API keys a provider_ids
API_KEYS = {
    os.getenv('PROVIDER_1_API_KEY'): 1,
    os.getenv('PROVIDER_2_API_KEY'): 2,
    os.getenv('PROVIDER_3_API_KEY'): 3
}

async def get_api_key(api_key: str = Depends(api_key_header)) -> int:
    """Valida la API key y retorna el provider_id asociado"""
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="API key inválida"
        )
    return API_KEYS[api_key]

def get_cache_key(provider_id: int, fecha: str) -> str:
    """Genera la clave para el caché"""
    return f"metricas:{provider_id}:{fecha}"

@app.get(
    "/metricas",
    response_model=List[MetricasResponse],
    responses={
        200: {"description": "Métricas obtenidas exitosamente"},
        403: {"model": ErrorResponse, "description": "API key inválida"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)
async def get_metricas(
    fecha: str = None,
    provider_id: int = Depends(get_api_key)
):
    """
    Obtiene las métricas de ventas para un proveedor específico
    
    - **fecha**: Fecha opcional en formato YYYY-MM-DD. Si no se proporciona, se usa la fecha actual
    - **provider_id**: Se obtiene automáticamente de la API key
    """
    try:
        # Validar y establecer la fecha
        if not fecha:
            fecha = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"Consultando métricas para proveedor {provider_id} en fecha {fecha}")
        
        # Intentar obtener del caché primero
        cache_key = get_cache_key(provider_id, fecha)
        # TODO: Implementar lógica de caché con ElastiCache
        
        # Consultar DynamoDB
        response = table.query(
            KeyConditionExpression=Key('id').begins_with(f"{provider_id}#") & Key('fecha').eq(fecha)
        )
        
        # Transformar resultados
        metricas = []
        for item in response['Items']:
            # Parsear la clave compuesta
            _, cliente_id, fecha = item['id'].split('#')
            
            metrica = MetricasResponse(
                cliente_id=cliente_id,
                fecha=fecha,
                num_transacciones=item['num_transacciones'],
                monto_total=float(item['monto_total'])
            )
            metricas.append(metrica)
            
        logger.info(f"Se encontraron {len(metricas)} registros")
        return metricas
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 