import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(
    format='%(asctime)s - %(taskName)s - %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%d/%m/%Y %H:%M:%S %z'
)

async def atender_topico_1(contenido):
    logging.info(f"Mensjae en Topico_1: {contenido}")

async def atender_topico_2(contenido):
    logging.info(f"Mensjae en Topico_2: {contenido}")

async def main():
    # Obtener variables de entorno
    servidor = os.environ.get('SERVIDOR')
    topico_1 = os.environ.get('TOPICO_1')
    topico_2 = os.environ.get('TOPICO_2')
    topico_publicar = os.environ.get('TOPICO_PUBLICAR')

    # Configuración MQTTS
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    #Unico cliente MQTT
    async with aiomqtt.Client(servidor, port=8883, tls_context=tls_context) as client:

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
