from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.main import app

@patch("src.main.conectar_banco", new_callable=AsyncMock)
@patch("src.main.iniciar_consumidor")
def test_api_health_check_retorna_status_ok(mock_consumidor, mock_conectar_banco):
    with TestClient(app) as client:
        response = client.get("/health")
        
        assert response.status_code == 200
        dados = response.json()
        
        assert dados["status"] == "operacional"
        assert dados["modulo"] == "M7 - Analytics"
        assert dados["broker_conectado"] is True