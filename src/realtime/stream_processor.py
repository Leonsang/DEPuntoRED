import json
import boto3
import logging
import psycopg2
from datetime import datetime
from typing import Dict, Any
from ..config.settings import DB_CONFIG, AWS_CONFIG
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamProcessor:
    def __init__(self):
        """Inicializa las conexiones a servicios AWS y RDS"""
        self.kinesis = boto3.client('kinesisanalytics')
        self.cloudwatch = boto3.client('cloudwatch')
        self.setup_db_connection()

    def setup_db_connection(self):
        """Configura la conexión a la base de datos"""
        try:
            self.conn = psycopg2.connect(
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            self.cursor = self.conn.cursor()
            logger.info("Conexión a base de datos establecida")
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {str(e)}")
            raise

    def extract_data(self):
        """Extrae datos de ventas desde RDS"""
        try:
            query = """
                SELECT 
                    cliente_id,
                    producto,
                    monto,
                    fecha
                FROM ventas
                WHERE fecha >= NOW() - INTERVAL '1 minute'
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            for row in rows:
                self.send_to_kinesis(row)
                
            logger.info(f"Extraídos y enviados {len(rows)} registros")
            
        except Exception as e:
            logger.error(f"Error extrayendo datos: {str(e)}")
            self.send_alert("Error en extracción de datos", str(e))
            raise

    def send_to_kinesis(self, row):
        """Envía datos al stream de entrada de Kinesis Analytics"""
        try:
            data = {
                'cliente_id': row[0],
                'producto': row[1],
                'monto': float(row[2]),
                'fecha': row[3].isoformat()
            }
            
            self.kinesis.put_record(
                ApplicationName=AWS_CONFIG['kinesis_app_name'],
                Input={
                    'NamePrefix': 'VENTAS_INPUT_STREAM',
                    'InputSchemaUpdate': {
                        'RecordFormat': {
                            'RecordFormatType': 'JSON'
                        }
                    },
                    'Records': [{'Data': json.dumps(data)}]
                }
            )
            
        except Exception as e:
            logger.error(f"Error enviando a Kinesis: {str(e)}")
            self.send_alert("Error en envío a Kinesis", str(e))

    def send_alert(self, title: str, message: str):
        """Envía una alerta a CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='PuntoRed/RealTime',
                MetricData=[{
                    'MetricName': 'ProcessingError',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [{
                        'Name': 'ErrorType',
                        'Value': title
                    }]
                }]
            )
            logger.error(f"{title}: {message}")
        except Exception as e:
            logger.error(f"Error enviando alerta: {str(e)}")

    def run(self):
        """Ejecuta el proceso de extracción continuamente"""
        try:
            while True:
                self.extract_data()
                time.sleep(60)  # Espera 1 minuto entre extracciones
        except KeyboardInterrupt:
            logger.info("Proceso detenido por el usuario")
        except Exception as e:
            logger.error(f"Error en el proceso principal: {str(e)}")
            self.send_alert("Error crítico", str(e))
        finally:
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    processor = StreamProcessor()
    processor.run() 