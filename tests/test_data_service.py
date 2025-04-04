import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.data_service import DataService

@pytest.fixture
def mock_db():
    """Fixture para simular la base de datos"""
    return Mock()

@pytest.fixture
def data_service(mock_db):
    """Fixture para el servicio de datos con DB mockeada"""
    with patch('src.services.data_service.create_engine') as mock_engine:
        mock_engine.return_value = mock_db
        service = DataService()
        service.engine = mock_db
        return service

def test_get_daily_transactions(data_service, mock_db):
    """Test para obtener transacciones diarias"""
    # Arrange
    expected_data = [
        {"cliente": "Juan Pérez", "cantidad_transacciones": 5, "monto_total": 500.0},
        {"cliente": "María López", "cantidad_transacciones": 3, "monto_total": 300.0}
    ]
    mock_db.execute.return_value.fetchall.return_value = expected_data
    
    # Act
    result = data_service.get_daily_transactions("producto1", "2024-03-21")
    
    # Assert
    assert result["producto"] == "producto1"
    assert result["fecha"] == "2024-03-21"
    assert len(result["transacciones"]) == 2

def test_get_top_clients(data_service, mock_db):
    """Test para obtener top clientes"""
    # Arrange
    expected_data = [
        {"cliente": "Juan Pérez", "monto_total": 1000.0},
        {"cliente": "María López", "monto_total": 800.0}
    ]
    mock_db.execute.return_value.fetchall.return_value = expected_data
    
    # Act
    result = data_service.get_top_clients(limit=2)
    
    # Assert
    assert len(result) == 2
    assert result[0]["monto_total"] > result[1]["monto_total"]

def test_cache_functionality(data_service):
    """Test para verificar funcionalidad de caché"""
    # Arrange
    test_data = {"test": "data"}
    cache_key = "test_key"
    
    # Act
    data_service.cache[cache_key] = test_data
    result = data_service.cache.get(cache_key)
    
    # Assert
    assert result == test_data

def test_error_handling(data_service, mock_db):
    """Test para manejo de errores"""
    # Arrange
    mock_db.execute.side_effect = Exception("DB Error")
    
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        data_service.get_daily_transactions("producto1")
    assert "DB Error" in str(exc_info.value)

def test_retry_mechanism(data_service, mock_db):
    """Test para mecanismo de reintentos"""
    # Arrange
    mock_db.execute.side_effect = [
        Exception("First try"),
        Exception("Second try"),
        Mock(fetchall=lambda: [{"success": True}])
    ]
    
    # Act
    result = data_service.get_daily_transactions("producto1")
    
    # Assert
    assert result is not None
    assert mock_db.execute.call_count == 3 