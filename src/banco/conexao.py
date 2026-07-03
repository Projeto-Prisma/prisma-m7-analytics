import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("M7_MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("M7_MONGODB_DB", "analytics")

class Database:
    client: AsyncIOMotorClient = None
    db = None

# Instância global para ser importada em outros arquivos
db = Database()

async def conectar_banco():
    print(f"[M7] Conectando ao MongoDB em {MONGODB_URL}...")
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.db = db.client[MONGODB_DB]
    
    # Faz um "ping" para garantir que o banco está vivo
    await db.client.admin.command('ping')
    print("[M7] MongoDB conectado com sucesso!")

async def fechar_conexao():
    if db.client:
        db.client.close()
        print("[M7] Conexão com MongoDB encerrada.")