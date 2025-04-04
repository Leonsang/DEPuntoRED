import os
import pandas as pd
from datetime import datetime, timedelta
import boto3
import logging
from sqlalchemy import create_engine
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyProcessor:
    def __init__(self):
        """Inicializa las conexiones y configuraciones necesarias"""
        self.rds_connection = create_engine(os.getenv('DATABASE_URL'))
        self.s3_client = boto3.client('s3')
        self.sns_client = boto3.client('sns')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.sns_topic = os.getenv('SNS_TOPIC_ARN')

    def extract_data(self, provider_id):
        """Extrae datos de RDS para un proveedor específico"""
        try:
            query = """
                SELECT 
                    c.id as cliente_id,
                    c.nombre,
                    c.apellido,
                    DATE(v.fecha) as fecha,
                    COUNT(*) as num_transacciones,
                    SUM(v.monto) as monto_total
                FROM clientes c
                JOIN ventas v ON c.id = v.cliente_id
                WHERE v.producto = :producto
                AND v.fecha >= CURRENT_DATE - INTERVAL '1 day'
                GROUP BY c.id, c.nombre, c.apellido, DATE(v.fecha)
            """
            
            df = pd.read_sql(
                query, 
                self.rds_connection,
                params={'producto': f'PRODUCTO_{provider_id}'}
            )
            logger.info(f"Datos extraídos exitosamente para proveedor {provider_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error en la extracción de datos: {str(e)}")
            self.send_notification(f"Error en extracción: {str(e)}")
            raise

    def transform_data(self, df, provider_id):
        """Transforma los datos según requerimientos del proveedor"""
        try:
            # Formato requerido por el proveedor
            result = {
                'provider_id': provider_id,
                'fecha_proceso': datetime.now().strftime('%Y-%m-%d'),
                'datos': df.to_dict(orient='records')
            }
            
            logger.info(f"Datos transformados exitosamente para proveedor {provider_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error en la transformación de datos: {str(e)}")
            self.send_notification(f"Error en transformación: {str(e)}")
            raise

    def load_data(self, data, provider_id):
        """Carga los datos procesados en S3"""
        try:
            fecha = datetime.now().strftime('%Y-%m-%d')
            key = f'provider_{provider_id}/fecha={fecha}/datos.json'
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            
            logger.info(f"Datos cargados exitosamente en S3 para proveedor {provider_id}")
            
        except Exception as e:
            logger.error(f"Error en la carga de datos: {str(e)}")
            self.send_notification(f"Error en carga: {str(e)}")
            raise

    def send_notification(self, message):
        """Envía notificación a través de SNS"""
        try:
            self.sns_client.publish(
                TopicArn=self.sns_topic,
                Message=message,
                Subject='Notificación Pipeline Batch'
            )
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")

    def process_provider(self, provider_id):
        """Procesa los datos para un proveedor específico"""
        try:
            # Extracción
            df = self.extract_data(provider_id)
            
            # Transformación
            transformed_data = self.transform_data(df, provider_id)
            
            # Carga
            self.load_data(transformed_data, provider_id)
            
            self.send_notification(f"Procesamiento exitoso para proveedor {provider_id}")
            
        except Exception as e:
            logger.error(f"Error en el procesamiento para proveedor {provider_id}: {str(e)}")
            raise

def lambda_handler(event, context):
    """Handler para AWS Lambda"""
    try:
        processor = DailyProcessor()
        
        # Procesar para cada proveedor
        for provider_id in range(1, 4):  # 3 proveedores
            processor.process_provider(provider_id)
            
        return {
            'statusCode': 200,
            'body': json.dumps('Procesamiento batch completado exitosamente')
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error en el procesamiento: {str(e)}')
        }

if __name__ == "__main__":
    # Para pruebas locales
    lambda_handler({}, None) 