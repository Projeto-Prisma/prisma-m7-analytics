import threading
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.banco.conexao import conectar_banco, fechar_conexao, db
from src.mensageria.consumidor import iniciar_consumidor

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de Ciclo de Vida da API."""
    print("[M7] Inicializando módulo de Analytics (CQRS)...")
    
    try:
        await conectar_banco()
        app.state.banco_conectado = True
    except Exception as e:
        print(f"[M7] Aviso: Não foi possível ligar ao MongoDB: {e}")
        app.state.banco_conectado = False

    print("[M7] A subir o consumidor RabbitMQ em background...")
    try:
        main_loop = asyncio.get_running_loop()
        thread_consumidor = threading.Thread(
            target=iniciar_consumidor, 
            args=(main_loop,), 
            daemon=True
        )
        thread_consumidor.start()
        app.state.broker_conectado = True
    except Exception as e:
        print(f"[M7] Aviso: Falha ao iniciar thread do RabbitMQ: {e}")
        app.state.broker_conectado = False
    
    yield
    
    await fechar_conexao()
    print("[M7] Encerrando módulo de Analytics...")

app = FastAPI(
    title="Prisma M7 - Analytics",
    description="Visão consolidada e inteligência urbana (CQRS)",
    lifespan=lifespan
)

# Essencial para permitir que a aplicação Web (React/Next.js) consuma a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "operacional",
        "modulo": "M7 - Analytics",
        "broker_conectado": app.state.broker_conectado,
        "banco_conectado": app.state.banco_conectado
    }

@app.get("/api/v1/analytics/mapa-calor")
async def obter_mapa_calor():
    """Retorna os clusters de recorrência para a renderização do mapa no Frontend."""
    if not app.state.banco_conectado or db.db is None:
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")
        
    cursor = db.db["clusters_view"].find({}, {"_id": 0})
    clusters = await cursor.to_list(length=1000)
    return {"clusters": clusters}

@app.get("/api/v1/analytics/kpis")
async def obter_kpis():
    """Retorna indicadores chave de desempenho para o dashboard de gestão."""
    if not app.state.banco_conectado or db.db is None:
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")
        
    total_denuncias = await db.db["denuncias_view"].count_documents({})
    total_clusters = await db.db["clusters_view"].count_documents({})
    
    # Aggregation Pipeline do MongoDB: agrupa as denúncias por categoria para o ranking
    pipeline = [
        {"$group": {"_id": "$categoria", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_categorias_cursor = db.db["denuncias_view"].aggregate(pipeline)
    top_categorias = await top_categorias_cursor.to_list(length=5)
    
    return {
        "total_denuncias": total_denuncias,
        "total_clusters": total_clusters,
        "top_categorias": [
            {"categoria": c["_id"], "quantidade": c["count"]} 
            for c in top_categorias if c["_id"] is not None
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)