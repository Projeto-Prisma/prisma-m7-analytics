from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from src.banco.conexao import conectar_banco, fechar_conexao

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de Ciclo de Vida da API."""
    print("[M7] Inicializando módulo de Analytics (CQRS)...")
    
    # 1. Tenta iniciar a conexão com o MongoDB
    try:
        await conectar_banco()
        app.state.banco_conectado = True
    except Exception as e:
        print(f"[M7] Aviso: Não foi possível conectar ao MongoDB localmente: {e}")
        app.state.banco_conectado = False

    # TODO: Iniciar Thread do Consumidor RabbitMQ 
    app.state.broker_conectado = True  # Mock mantido para a infra não reiniciar
    
    yield
    
    # 2. Fecha a conexão ao desligar
    await fechar_conexao()
    print("[M7] Encerrando módulo de Analytics...")

app = FastAPI(
    title="Prisma M7 - Analytics",
    description="Visão consolidada e inteligência urbana (CQRS)",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    """Endpoint monitorado pelo start.sh da infraestrutura."""
    return {
        "status": "operacional",
        "modulo": "M7 - Analytics",
        "broker_conectado": app.state.broker_conectado,
        "banco_conectado": app.state.banco_conectado
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)