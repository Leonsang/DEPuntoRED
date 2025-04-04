import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.api.main import app
from src.config.settings import API_CONFIG

client = TestClient(app)

@pytest.fixture
def mock_data_service():
    """Fixture para mockear el servicio de datos"""
    with patch('src.api.main.DataService') as mock:
        yield mock.return_value

def test_health_check():
    """Test del endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_transacciones_success(mock_data_service):
    """Test exitoso del endpoint de transacciones"""
    # Arrange
    expected_data = {
        "producto": "producto1",
        "fecha": "2024-03-21",
        "transacciones": [
            {"cliente": "Juan Pérez", "cantidad": 5, "monto": 500.0}
        ]
    }
    mock_data_service.get_daily_transactions.return_value = expected_data
    
    # Act
    response = client.get(
        "/transacciones",
        params={"producto": "producto1", "fecha": "2024-03-21"},
        headers={"X-API-Key": API_CONFIG["api_key"]}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["data"] == expected_data

def test_get_transacciones_sin_auth():
    """Test de transacciones sin autenticación"""
    response = client.get("/transacciones", params={"producto": "producto1"})
    assert response.status_code == 403

def test_get_top_clientes(mock_data_service):
    """Test del endpoint de top clientes"""
    # Arrange
    expected_data = [
        {"cliente": "Juan Pérez", "monto_total": 1000.0},
        {"cliente": "María López", "monto_total": 800.0}
    ]
    mock_data_service.get_top_clients.return_value = expected_data
    
    # Act
    response = client.get(
        "/top-clientes",
        params={"limit": 2},
        headers={"X-API-Key": API_CONFIG["api_key"]}
    )
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

def test_validacion_parametros():
    """Test de validación de parámetros"""
    response = client.get(
        "/top-clientes",
        params={"limit": -1},
        headers={"X-API-Key": API_CONFIG["api_key"]}
    )
    assert response.status_code == 400

def test_manejo_errores(mock_data_service):
    """Test de manejo de errores"""
    # Arrange
    mock_data_service.get_daily_transactions.side_effect = Exception("Error de prueba")
    
    # Act
    response = client.get(
        "/transacciones",
        params={"producto": "producto1"},
        headers={"X-API-Key": API_CONFIG["api_key"]}
    )
    
    # Assert
    assert response.status_code == 500
    assert "Error de prueba" in response.json()["detail"] 