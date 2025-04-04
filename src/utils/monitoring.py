import logging
import time
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Callable
import boto3
from src.config.settings import MONITORING_CONFIG

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cliente de CloudWatch
cloudwatch = boto3.client('cloudwatch')

def log_execution_time(func: Callable) -> Callable:
    """Decorador para medir y registrar el tiempo de ejecución de funciones"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log local
        logger.info(f"Función {func.__name__} ejecutada en {execution_time:.2f} segundos")
        
        # Métrica en CloudWatch
        cloudwatch.put_metric_data(
            Namespace='PuntoRed/Analytics',
            MetricData=[{
                'MetricName': 'FunctionExecutionTime',
                'Value': execution_time,
                'Unit': 'Seconds',
                'Dimensions': [{'Name': 'FunctionName', 'Value': func.__name__}]
            }]
        )
        
        return result
    return wrapper

def monitor_transactions(transactions_count: int, error_count: int = 0) -> None:
    """Registra métricas de transacciones procesadas"""
    timestamp = datetime.utcnow()
    
    metrics = [
        {
            'MetricName': 'ProcessedTransactions',
            'Value': transactions_count,
            'Unit': 'Count',
            'Timestamp': timestamp
        },
        {
            'MetricName': 'ProcessingErrors',
            'Value': error_count,
            'Unit': 'Count',
            'Timestamp': timestamp
        },
        {
            'MetricName': 'SuccessRate',
            'Value': (transactions_count - error_count) / max(transactions_count, 1) * 100,
            'Unit': 'Percent',
            'Timestamp': timestamp
        }
    ]
    
    cloudwatch.put_metric_data(
        Namespace='PuntoRed/Analytics',
        MetricData=metrics
    )

def log_api_request(endpoint: str, response_time: float, status_code: int) -> None:
    """Registra métricas de las solicitudes a la API"""
    cloudwatch.put_metric_data(
        Namespace='PuntoRed/API',
        MetricData=[
            {
                'MetricName': 'APILatency',
                'Value': response_time,
                'Unit': 'Milliseconds',
                'Dimensions': [{'Name': 'Endpoint', 'Value': endpoint}]
            },
            {
                'MetricName': 'RequestCount',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Endpoint', 'Value': endpoint},
                    {'Name': 'StatusCode', 'Value': str(status_code)}
                ]
            }
        ]
    )

def create_alarm(
    metric_name: str,
    threshold: float,
    comparison_operator: str,
    evaluation_periods: int = 1
) -> None:
    """Crea una alarma en CloudWatch"""
    cloudwatch.put_metric_alarm(
        AlarmName=f'PuntoRed-{metric_name}-Alarm',
        MetricName=metric_name,
        Namespace='PuntoRed/Analytics',
        ComparisonOperator=comparison_operator,
        Threshold=threshold,
        EvaluationPeriods=evaluation_periods,
        Period=300,  # 5 minutos
        Statistic='Average',
        ActionsEnabled=True,
        AlarmActions=[MONITORING_CONFIG['sns_topic_arn']]
    )

# Configuración inicial de alarmas
def setup_monitoring():
    """Configura las alarmas iniciales del sistema"""
    create_alarm(
        metric_name='ProcessingErrors',
        threshold=10,
        comparison_operator='GreaterThanThreshold'
    )
    
    create_alarm(
        metric_name='SuccessRate',
        threshold=95,
        comparison_operator='LessThanThreshold'
    )
    
    create_alarm(
        metric_name='APILatency',
        threshold=1000,  # 1 segundo
        comparison_operator='GreaterThanThreshold'
    ) 