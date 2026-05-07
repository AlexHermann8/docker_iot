import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(
    format='%(asctime)s - %(taskName)s - %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%d/%m/%Y %H:%M:%S %z'
)

async def atender_topico_1(contenido):
    logging.info(f"Mensaje en Topico_1: {contenido}")

async def atender_topico_2(contenido):
    logging.info(f"Mensaje en Topico_2: {contenido}")

async def incrementar_contador(contador):
    """Suma 1 cada 3 segundos"""
    while True:
        await asyncio.sleep(3)
        contador[0] += 1 # Modificamos el interior de la lista
        logging.info(f"Contador incrementado a: {contador[0]}")

async def publicar_contador(client, contador, topico):
    """Publica el contador cada 5 segundos"""
    while True:
        await asyncio.sleep(5)
        valor = str(contador[0])
        await client.publish(topico, payload=valor)
        logging.info(f"Publicado {valor} en {topico}")

async def main():
    # Obtener variables de entorno
    servidor = os.environ.get('SERVIDOR')
    topico_1 = os.environ.get('TOPICO_1')
    topico_2 = os.environ.get('TOPICO_2')
    topico_publicar = os.environ.get('TOPICO_PUBLICAR')

    # Contador
    contador = [0] # Lista para permitir la modificación dentro de las tareas

    # Configuración MQTTS
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    #Unico cliente MQTT
    async with aiomqtt.Client(servidor, port=8883, tls_context=tls_context) as client:

        # Iniciar tareas
        asyncio.create_task(incrementar_contador(contador), name="Tarea-Contador")
        asyncio.create_task(publicar_contador(client, contador, topico_publicar), name="Tarea-Publicar-Contador")

        # Suscribirse a los tópicos
        await client.subscribe(topico_1)
        await client.subscribe(topico_2)

        async for message in client.messages:
            contenido = message.payload.decode("utf-8") 

            if str(message.topic) == topico_1:
                asyncio.create_task(
                    atender_topico_1(contenido),
                    name="Tarea-Suscripcion-1"
                )
            elif str(message.topic) == topico_2:
                asyncio.create_task(
                    atender_topico_2(contenido),
                    name="Tarea-Suscripcion-2"
                )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Programa detenido por el usuario")
