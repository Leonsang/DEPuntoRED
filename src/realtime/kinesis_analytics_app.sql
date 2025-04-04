-- Crear stream de entrada
CREATE OR REPLACE STREAM "VENTAS_INPUT_STREAM" (
    cliente_id INTEGER,
    producto VARCHAR(50),
    monto DOUBLE,
    fecha TIMESTAMP
);

-- Crear stream de salida para métricas agregadas
CREATE OR REPLACE STREAM "METRICAS_OUTPUT_STREAM" (
    id VARCHAR(100),
    cliente_id INTEGER,
    producto VARCHAR(50),
    num_transacciones INTEGER,
    monto_total DOUBLE,
    fecha_hora TIMESTAMP
);

-- Crear bomba de datos para escribir a DynamoDB
CREATE OR REPLACE PUMP "METRICAS_PUMP" AS
    INSERT INTO "METRICAS_OUTPUT_STREAM"
    -- Agregación continua por cliente, producto y fecha
    SELECT 
        CONCAT(CAST(cliente_id AS VARCHAR), '#', 
               producto, '#',
               DATE_FORMAT(FLOOR(ventas.ROWTIME TO MINUTE), '%Y-%m-%d')) AS id,
        cliente_id,
        producto,
        COUNT(*) AS num_transacciones,
        SUM(monto) AS monto_total,
        FLOOR(ventas.ROWTIME TO MINUTE) AS fecha_hora
    FROM "VENTAS_INPUT_STREAM" AS ventas
    -- Ventana de 1 minuto para agregaciones en tiempo real
    GROUP BY 
        FLOOR(ventas.ROWTIME TO MINUTE),
        cliente_id,
        producto;

-- Crear alertas para monitoreo
CREATE OR REPLACE STREAM "ALERTAS_STREAM" (
    mensaje VARCHAR(1000),
    nivel VARCHAR(20),
    fecha_hora TIMESTAMP
);

-- Monitorear transacciones grandes
INSERT INTO "ALERTAS_STREAM"
SELECT 
    CONCAT('Transacción grande detectada: Cliente ', CAST(cliente_id AS VARCHAR), ' - Monto: ', CAST(monto AS VARCHAR)) AS mensaje,
    'WARN' AS nivel,
    CURRENT_TIMESTAMP AS fecha_hora
FROM "VENTAS_INPUT_STREAM"
WHERE monto > 1000; 