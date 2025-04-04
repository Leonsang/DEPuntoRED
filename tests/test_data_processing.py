import pytest
from datetime import datetime
from src.processing.data_processor import DataProcessor
from src.models.transaction import Transaction

@pytest.fixture
def sample_transactions():
    """Fixture que proporciona datos de prueba"""
    return [
        Transaction(
            id="1",
            cliente="Juan Pérez",
            producto="Producto1",
            cantidad=2,
            monto=200.0,
            fecha=datetime(2024, 3, 21)
        ),
        Transaction(
            id="2",
            cliente="María López",
            producto="Producto1",
            cantidad=3,
            monto=300.0,
            fecha=datetime(2024, 3, 21)
        )
    ]

@pytest.fixture
def data_processor():
    """Fixture que proporciona una instancia del procesador de datos"""
    return DataProcessor()

def test_calcular_total_diario(data_processor, sample_transactions):
    """Test del cálculo de totales diarios"""
    # Act
    resultado = data_processor.calcular_total_diario(sample_transactions)
    
    # Assert
    assert resultado["total_transacciones"] == 2
    assert resultado["monto_total"] == 500.0
    assert resultado["cantidad_total"] == 5

def test_agrupar_por_cliente(data_processor, sample_transactions):
    """Test de agrupación por cliente"""
    # Act
    resultado = data_processor.agrupar_por_cliente(sample_transactions)
    
    # Assert
    assert len(resultado) == 2
    assert resultado["Juan Pérez"] == 200.0
    assert resultado["María López"] == 300.0

def test_calcular_promedio_ticket(data_processor, sample_transactions):
    """Test del cálculo de ticket promedio"""
    # Act
    promedio = data_processor.calcular_promedio_ticket(sample_transactions)
    
    # Assert
    assert promedio == 250.0  # (200 + 300) / 2

def test_filtrar_por_fecha(data_processor, sample_transactions):
    """Test de filtrado por fecha"""
    # Arrange
    fecha = datetime(2024, 3, 21)
    
    # Act
    filtrados = data_processor.filtrar_por_fecha(sample_transactions, fecha)
    
    # Assert
    assert len(filtrados) == 2
    assert all(t.fecha == fecha for t in filtrados)

def test_validar_transaccion():
    """Test de validación de transacciones"""
    # Arrange
    transaccion_valida = Transaction(
        id="1",
        cliente="Juan Pérez",
        producto="Producto1",
        cantidad=2,
        monto=200.0,
        fecha=datetime.now()
    )
    
    transaccion_invalida = Transaction(
        id="2",
        cliente="",  # Cliente vacío
        producto="Producto1",
        cantidad=-1,  # Cantidad negativa
        monto=0,  # Monto cero
        fecha=datetime.now()
    )
    
    # Act & Assert
    assert DataProcessor.validar_transaccion(transaccion_valida) == True
    assert DataProcessor.validar_transaccion(transaccion_invalida) == False

def test_procesar_lote_vacio(data_processor):
    """Test de procesamiento de lote vacío"""
    # Act
    resultado = data_processor.calcular_total_diario([])
    
    # Assert
    assert resultado["total_transacciones"] == 0
    assert resultado["monto_total"] == 0.0
    assert resultado["cantidad_total"] == 0 