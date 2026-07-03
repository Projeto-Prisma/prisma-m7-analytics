from fastapi.testclient import TestClient
from src.main import app

def test_api_health_check_retorna_status_ok():
    with TestClient(app) as client:
        response = client.get("/health")
        
        assert response.status_code == 200
        dados = response.json()
        
        assert dados["status"] == "operacional"
        assert dados["modulo"] == "M7 - Analytics"
        assert dados["broker_conectado"] is True