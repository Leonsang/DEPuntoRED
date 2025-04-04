# Respuestas Teóricas - Prueba Técnica Puntored

## Python

### 1. Diferencia entre lista y conjunto (set)
Una lista es una colección ordenada y mutable de elementos que permite duplicados, mientras que un conjunto es una colección no ordenada y mutable de elementos únicos.

Ejemplo:
```python
# Lista
lista = [1, 2, 2, 3, 4, 4]
print(lista)  # [1, 2, 2, 3, 4, 4]

# Conjunto
conjunto = {1, 2, 2, 3, 4, 4}
print(conjunto)  # {1, 2, 3, 4}
```

### 2. Generators en Python
Un generator es una función que produce una secuencia de valores usando `yield` en lugar de `return`. Es útil para:
- Procesar grandes volúmenes de datos sin cargarlos en memoria
- Crear secuencias infinitas
- Implementar pipelines de procesamiento

Ejemplo:
```python
def numeros_pares(n):
    for i in range(n):
        if i % 2 == 0:
            yield i

# Uso
for num in numeros_pares(10):
    print(num)  # 0, 2, 4, 6, 8
```

### 3. Ventajas de Pandas
- Estructuras de datos optimizadas (DataFrame, Series)
- Operaciones vectorizadas más rápidas
- Manejo eficiente de datos faltantes
- Funciones de agregación y transformación
- Integración con otras bibliotecas de análisis
- Indexación avanzada y selección de datos
- Manejo de fechas y tiempos
- Lectura/escritura de múltiples formatos

### 4. Diferencia entre apply() y map()
- `apply()`: Aplica una función a lo largo de un eje del DataFrame
- `map()`: Aplica una función a cada elemento de una Serie

Ejemplo:
```python
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# apply() - función por columna
df.apply(lambda x: x.max() - x.min(), axis=0)

# map() - función por elemento
df['A'].map(lambda x: x * 2)
```

## SQL

### 1. Consulta de salario promedio
```sql
SELECT 
    d.nombre as departamento,
    AVG(e.salario) as salario_promedio
FROM 
    departamentos d
JOIN 
    empleados e ON d.id = e.departamento_id
GROUP BY 
    d.id, d.nombre;
```

### 2. Diferencia entre JOINs
- `INNER JOIN`: Devuelve solo las filas que tienen coincidencias en ambas tablas
- `LEFT JOIN`: Devuelve todas las filas de la tabla izquierda y las coincidencias de la derecha
- `FULL JOIN`: Devuelve todas las filas de ambas tablas

Ejemplos:
```sql
-- INNER JOIN
SELECT e.nombre, d.nombre
FROM empleados e
INNER JOIN departamentos d ON e.departamento_id = d.id;

-- LEFT JOIN
SELECT e.nombre, d.nombre
FROM empleados e
LEFT JOIN departamentos d ON e.departamento_id = d.id;

-- FULL JOIN
SELECT e.nombre, d.nombre
FROM empleados e
FULL JOIN departamentos d ON e.departamento_id = d.id;
```

### 3. Optimización de consultas
- Crear índices apropiados
- Usar particionamiento
- Optimizar el diseño de tablas
- Usar EXPLAIN para analizar el plan de ejecución
- Evitar SELECT *
- Usar WHERE antes de GROUP BY
- Limitar el uso de subconsultas
- Mantener estadísticas actualizadas

### 4. HAVING vs WHERE
- `WHERE`: Filtra filas antes de la agregación
- `HAVING`: Filtra después de la agregación

Ejemplo:
```sql
-- WHERE filtra empleados con salario > 50000
SELECT departamento_id, AVG(salario)
FROM empleados
WHERE salario > 50000
GROUP BY departamento_id;

-- HAVING filtra departamentos con promedio > 50000
SELECT departamento_id, AVG(salario)
FROM empleados
GROUP BY departamento_id
HAVING AVG(salario) > 50000;
```

## Amazon Web Services

### 1. Diferencias entre S3, RDS y Redshift
- **S3**: Almacenamiento de objetos, ideal para archivos estáticos
- **RDS**: Base de datos relacional gestionada, para OLTP
- **Redshift**: Almacén de datos, optimizado para OLAP

### 2. Cuándo usar DynamoDB
- Cuando se necesita escalabilidad horizontal
- Para aplicaciones con patrones de acceso no relacionales
- Cuando la consistencia eventual es aceptable
- Para cargas de trabajo con alto rendimiento

### 3. Lambda vs EC2
- **Lambda**: Sin servidor, escala automáticamente, pago por uso
- **EC2**: Control completo, mejor para cargas de trabajo constantes

### 4. Acceso seguro a S3
- Usar IAM roles
- Implementar políticas de bucket
- Usar VPC endpoints
- Implementar encriptación
- Usar presigned URLs cuando sea necesario 