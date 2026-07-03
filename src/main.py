from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de Ciclo de Vida da API.
    Inicia conexões ao subir e as fecha ao desligar.
    """
    print("[M7] Inicializando módulo de Analytics (CQRS)...")
    # TODO: Iniciar conexão com MongoDB 
    # TODO: Iniciar Thread do Consumidor RabbitMQ 
    
    yield
    
    print("[M7] Encerrando módulo de Analytics...")


app = FastAPI(
    title="Prisma M7 - Analytics",
    description="Visão consolidada e inteligência urbana (CQRS)",
    lifespan=lifespan
)


@app.get("/health")
def health_check():
    """
    Endpoint de saúde consumido pela infraestrutura (start.sh).
    O script da infra monitora ativamente a flag 'broker_conectado'.
    """
    return {
        "status": "operacional",
        "modulo": "M7 - Analytics",
        "broker_conectado": True,  # Mock para o start.sh (será dinâmico no Commit 4)
        "banco_conectado": True    # Mock (será dinâmico no Commit 3)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)