import asyncio
from unittest.mock import patch, MagicMock
from src.banco.projecao import processar_evento_cqrs

def test_processar_evento_cqrs_nao_quebra():
    """Garante que a lógica central do CQRS suporta os dados sem causar crash."""
    dados = {"id": 123, "texto": "Buraco na via"}
    
    with patch("src.banco.projecao.db") as mock_db:
        mock_colecao = MagicMock()
        mock_db.db = {"denuncias_view": mock_colecao}
        
        asyncio.run(processar_evento_cqrs("denuncia.recebida", dados))
        
        assert True