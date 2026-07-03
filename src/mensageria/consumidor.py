import os
import json
import pika
import asyncio
from src.banco.projecao import processar_evento_cqrs

RABBITMQ_URL = os.getenv("M7_RABBITMQ_URL", "amqp://prisma:prisma_secret@localhost:5672/")
EXCHANGE = os.getenv("M7_EXCHANGE", "denuncias")
FILA = os.getenv("M7_FILA", "m7.analytics")
ROUTING_KEY = "#"  # Escuta tudo!

def iniciar_consumidor(main_loop):
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.queue_declare(queue=FILA, durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue=FILA, routing_key=ROUTING_KEY)

        def callback(ch, method, properties, body):
            try:
                evento = method.routing_key
                dados = json.loads(body)
                print(f"[M7] Mensagem recebida: {evento}")
                
                # Como a biblioteca Pika é síncrona e o MongoDB (motor) é assíncrono,
                # usamos o loop do FastAPI para injetar a tarefa de gravação sem travar a fila.
                if main_loop:
                    asyncio.run_coroutine_threadsafe(
                        processar_evento_cqrs(evento, dados), 
                        main_loop
                    )
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"[M7] Erro ao processar evento: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_qos(prefetch_count=10)
        
        print(f"[M7] Consumidor Universal Operacional. À escuta de '{ROUTING_KEY}'...")
        channel.basic_consume(queue=FILA, on_message_callback=callback)
        channel.start_consuming()
        
    except Exception as e:
        print(f"[M7] Erro crítico de mensageria: {e}")