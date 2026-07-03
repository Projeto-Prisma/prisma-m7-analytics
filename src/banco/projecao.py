from src.banco.conexao import db

async def processar_evento_cqrs(evento: str, dados: dict):
    """
    Motor CQRS: Recebe qualquer evento do sistema e atualiza a View no MongoDB.
    """
    try:
        # Se não houver ligação ao banco (testes locais rápidos), ignoramos a gravação
        if db.db is None:
            return

        payload = dados.get("payload", dados)
        
        # 1. Trata Eventos Geográficos/Clusters (Oriundos do M4 - Recorrência)
        if evento == "padrao.recorrencia":
            cluster_id = payload.get("regiao", {}).get("cluster_id")
            if cluster_id:
                colecao_clusters = db.db["clusters_view"]
                await colecao_clusters.update_one(
                    {"cluster_id": cluster_id},
                    {"$set": {
                        "categoria": payload.get("categoria"),
                        "contagem": payload.get("contagem"),
                        "janela_de_tempo": payload.get("janela_de_tempo"),
                        "centroide": payload.get("regiao", {}).get("centroide")
                    }},
                    upsert=True # Se não existir, cria. Se existir, atualiza.
                )
                print(f"[M7-CQRS] Mapa de calor do cluster {cluster_id} atualizado.")
            return

        # 2. Trata Eventos de Ciclo de Vida da Denúncia (M1, M2, M3, M5, M6)
        denuncia_id = payload.get("id") or dados.get("id")
        if denuncia_id:
            colecao_denuncias = db.db["denuncias_view"]
            
            # Estrutura base de atualização
            update_data = {
                "$set": {"ultima_atualizacao": evento, "status_atual": evento}
            }
            
            # Enriquece o documento conforme a jornada da denúncia avança
            if evento == "denuncia.recebida":
                update_data["$set"]["texto"] = payload.get("texto")
                update_data["$set"]["localizacao"] = payload.get("localizacao")
            elif evento == "denuncia.classificada":
                update_data["$set"]["categoria"] = payload.get("categoria")
            elif evento == "denuncia.priorizada":
                update_data["$set"]["prioridade_nivel"] = payload.get("nivel")
                update_data["$set"]["prioridade_score"] = payload.get("score")
            elif evento == "denuncia.encaminhada":
                update_data["$set"]["orgao_destino"] = payload.get("orgao_destino")
                
            await colecao_denuncias.update_one(
                {"id_denuncia": denuncia_id},
                update_data,
                upsert=True
            )
            print(f"[M7-CQRS] Denúncia {denuncia_id} agregada com sucesso (Evento: {evento})")

    except Exception as e:
        print(f"[Erro CQRS] Falha ao processar a projeção no MongoDB: {e}")