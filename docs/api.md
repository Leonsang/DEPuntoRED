# API REST - PuntoRed Analytics

## Tabla de Contenidos
- [Endpoints](#endpoints)
  - [Métricas por Cliente](#métricas-por-cliente)
  - [Métricas por Producto](#métricas-por-producto)
- [Seguridad](#seguridad)
- [Rendimiento](#rendimiento)
- [Ejemplos de Uso](#ejemplos-de-uso)

## Endpoints

### Métricas por Cliente
```
GET /metricas/cliente/{cliente_id}
```

#### Parámetros
- `cliente_id` (path): ID del cliente
- `producto` (query, opcional): Filtrar por producto
- `fecha` (query, opcional): Fecha en formato YYYY-MM-DD

#### Respuesta
```json
{
  "cliente_id": "integer",
  "metricas": {
    "num_transacciones": "integer",
    "monto_total": "decimal"
  }
}
```

[Ver implementación](src/api/main.py#L45)

### Métricas por Producto
```
GET /metricas/producto/{producto_id}
```

#### Parámetros
- `producto_id` (path): ID del producto
- `fecha` (query, opcional): Fecha en formato YYYY-MM-DD

#### Respuesta
```json
{
  "producto": "string",
  "metricas": {
    "num_transacciones": "integer",
    "monto_total": "decimal"
  }
}
```

[Ver implementación](src/api/main.py#L78)

## Seguridad

### Autenticación
- API Key requerida en header `X-API-Key`
- [Ver configuración de API Keys](deployment.md#api-keys)

### Rate Limiting
- Límite: 1000 peticiones por minuto
- [Ver configuración de rate limiting](deployment.md#rate-limiting)

### CORS
- Orígenes permitidos configurados
- [Ver configuración CORS](deployment.md#cors)

## Rendimiento

### Latencia
- Tiempo real: < 1 minuto
- Batch: < 5 minutos
- [Ver métricas de rendimiento](deployment.md#métricas)

### Caché
- TTL: 5 minutos
- [Ver configuración de caché](deployment.md#caché)

## Ejemplos de Uso

### Python
```python
import requests

headers = {
    'X-API-Key': 'tu-api-key'
}

# Obtener métricas de cliente
response = requests.get(
    'https://api.puntored.com/metricas/cliente/123',
    headers=headers,
    params={'producto': 'PRODUCTO_1'}
)
```

### cURL
```bash
curl -X GET \
  'https://api.puntored.com/metricas/producto/PRODUCTO_1' \
  -H 'X-API-Key: tu-api-key'
```

[Ver más ejemplos](examples/)

---

[Volver al índice](README.md) 