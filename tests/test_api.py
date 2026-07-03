import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from src.main import app

@patch("src.main.conectar_banco", new_callable=AsyncMock)
@patch("src.main.iniciar_consumidor")
@patch("src.main.db")
def test_obter_kpis_retorna_agregacoes_corretas(mock_db, mock_consumidor, mock_conectar_banco):
    """Garante que a agregação dos indicadores seja serializada no formato esperado pelo Frontend."""
    
    # 1. mocks específicos para cada coleção do MongoDB
    mock_colecao_denuncias = MagicMock()
    mock_colecao_clusters = MagicMock()
    
    # 2. o mock do banco foi ensinado a devolver a coleção correta quando chamada
    def get_collection(name):
        if name == "denuncias_view":
            return mock_colecao_denuncias
        if name == "clusters_view":
            return mock_colecao_clusters
        return MagicMock()
        
    mock_db.db.__getitem__.side_effect = get_collection
    
    # 3. count_documents e to_list são funções ASSÍNCRONAS
    mock_colecao_denuncias.count_documents = AsyncMock(return_value=150)
    mock_colecao_clusters.count_documents = AsyncMock(return_value=12)
    
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[{"_id": "Manutenção e Limpeza Urbana", "count": 50}])
    mock_colecao_denuncias.aggregate.return_value = mock_cursor

    # 4. Executa a requisição
    with TestClient(app) as client:
        # Quando mockado, o lifespan seta a variável como True corretamente
        response = client.get("/api/v1/analytics/kpis")
        
        assert response.status_code == 200
        dados = response.json()
        
        assert dados["total_denuncias"] == 150
        assert dados["total_clusters"] == 12
        assert dados["top_categorias"][0]["categoria"] == "Manutenção e Limpeza Urbana"
        assert dados["top_categorias"][0]["quantidade"] == 50