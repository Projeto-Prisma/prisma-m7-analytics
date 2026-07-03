import os
import json
import pika

RABBITMQ_URL = os.getenv("M7_RABBITMQ_URL", "amqp://prisma:prisma_secret@localhost:5672/")
EXCHANGE = os.getenv("M7_EXCHANGE", "denuncias")
FILA = os.getenv("M7_FILA", "m7.analytics")
ROUTING_KEY = "#"  # O coração do CQRS: escuta TODOS os eventos do sistema

def iniciar_consumidor():
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declara o exchange e a fila durável
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.queue_declare(queue=FILA, durable=True)
        
        # Faz o bind usando o curinga '#'
        channel.queue_bind(exchange=EXCHANGE, queue=FILA, routing_key=ROUTING_KEY)

        def callback(ch, method, properties, body):
            try:
                evento = method.routing_key
                dados = json.loads(body)
                print(f"[M7-CQRS] Evento capturado: '{evento}' -> Dados: {dados.get('id', 'N/A')}")
                
                # TODO: Passar o evento para o motor de projeção do MongoDB (Commit 5)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"[M7-CQRS] Erro ao processar evento: {e}")
                # Rejeita sem requeue para evitar loops infinitos de erro
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # O M7 pode processar lotes maiores porque fará apenas inserções/atualizações no Mongo
        channel.basic_qos(prefetch_count=10)
        
        print(f"[M7] Consumidor Universal Operacional. A escutar '{ROUTING_KEY}' em '{FILA}'...")
        channel.basic_consume(queue=FILA, on_message_callback=callback)
        channel.start_consuming()
        
    except Exception as e:
        print(f"[M7] Erro crítico de mensageria (RabbitMQ desligado localmente?): {e}")