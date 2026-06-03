from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging, os, asyncio, aiomysql, traceback, locale
import matplotlib.pyplot as plt
from io import BytesIO
import aiomqtt, ssl

# Configuracion de bot, servidor MQTT e id_dispositivo
token=os.environ["TB_TOKEN"]
servidor = os.environ['SERVIDOR']
ID_DISPOSITIVO = "1324"

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Función para la conexión y publicación en MQTT
async def publicar_mqtt(topico, payload):

     # Configuración MQTTS
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    try:
        async with aiomqtt.Client(
            hostname=os.environ['SERVIDOR'],
            port=int(os.environ['PUERTO_MQTTS']),    
            tls_context=tls_context
        ) as client:
            await client.publish(topico, payload=str(payload))
            logging.info(f"Éxito: Publicado '{payload}' en el tópico '{topico}'")
            return True
    except Exception as e:
        logging.error(f"Error al conectar o publicar en MQTT: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("se conectó: " + str(update.message.from_user.id))
    if update.message.from_user.first_name:
        nombre=update.message.from_user.first_name
    else:
        nombre=""
    if update.message.from_user.last_name:
        apellido=update.message.from_user.last_name
    else:
        apellido=""
    kb = [
        ["modo auto","modo manual"],
        ["rele ON","rele OFF"],
        ["destello"]
        ]
    await context.bot.send_message(
        update.message.chat.id,
        text="Bienvenido al Bot "+ nombre + " " + apellido,
        reply_markup=ReplyKeyboardMarkup(kb)
    )

async def acercade(update: Update, context):
    await context.bot.send_message(update.message.chat.id, text="Este bot fue creado para el curso de IoT FIO")

async def baile(update: Update, context):
    logging.info(context.args)
    if context.args and context.args[0] == '@baile':
        await context.bot.send_animation(update.message.chat.id, "CgACAgQAAxkBAAMHahiDeEYT2bwwLaOI9QVooA-adRcAAs0GAAK6K4RSN3xbqs1Aooo7BA")
        await asyncio.sleep(6)
        await context.bot.send_message(update.message.chat.id, text="¡Patito feliz!")
    else:
        await context.bot.send_message(update.message.chat.id, text="¡No puede bailar!")

async def setpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Falta el valor de setpoint. Ejemplo: /setpoint 24.5")
        return
    valor = context.args[0]
    topico = f"{ID_DISPOSITIVO}/setpoint"
    await update.message.reply_text(f"Enviando setpoint: {valor}°C...")
    if await publicar_mqtt(topico, valor):
        await update.message.reply_text(f"Setpoint enviado: {valor}°C")
    else:
        await update.message.reply_text("Error al publicar en MQTT.")

async def modo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recibido = update.message.text

    # "Modo Auto" -> "1", "Modo Manual" -> "0"
    valor = "1" if texto_recibido == "modo auto" else "0"
    topico = f"{ID_DISPOSITIVO}/modo"

    await update.message.reply_text(f"Cambiando a {texto_recibido}...")
    if await publicar_mqtt(topico, valor):
        await update.message.reply_text(f"Termostato configurado en {texto_recibido}.")
    else:
        await update.message.reply_text("Error al publicar en MQTT.")

async def rele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recibido = update.message.text

    # "Relé ON" -> "0" (Encender), "Relé OFF" -> "1" (Apagar)
    valor = "0" if texto_recibido == "rele ON" else "1"
    topico = f"{ID_DISPOSITIVO}/rele"

    await update.message.reply_text(f"Enviando orden: {texto_recibido}...")
    if await publicar_mqtt(topico, valor):
        await update.message.reply_text(f"Comando {texto_recibido} enviado.\n*(Solo se aplica si está en Modo Manual)*")
    else:
        await update.message.reply_text("Error al publicar en MQTT.")

async def destello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topico = f"{ID_DISPOSITIVO}/destello"

    await update.message.reply_text("Solicitando destello a la Pico...")
    if await publicar_mqtt(topico, "destello"):
        await update.message.reply_text("Comando Destello enviado!")
    else:
        await update.message.reply_text("Error al publicar en MQTT.")

def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('acercade', acercade))
    application.add_handler(CommandHandler('baile', baile))
    application.add_handler(CommandHandler('setpoint', setpoint))

    application.add_handler(MessageHandler(filters.Regex("^(modo auto|modo manual)$"), modo))
    application.add_handler(MessageHandler(filters.Regex("^(rele ON|rele OFF)$"), rele))
    application.add_handler(MessageHandler(filters.Regex("^(destello)$"), destello))
    
    application.run_polling()

if __name__ == '__main__':
    main()
