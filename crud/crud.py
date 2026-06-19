from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix
import os, logging, ssl
import paho.mqtt.client as mqtt

logging.basicConfig(format='%(asctime)s - CRUD - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.secret_key = os.environ["FLASK_SECRET_KEY"]

def publicar_mqtt(topico, payload):
    servidor = os.environ["SERVIDOR"]
    puerto = int(os.environ["PUERTO_MQTT"])

    try:
        contexto_tls = ssl.create_default_context()
        client = mqtt.Client()
        client.tls_set_context(contexto_tls)

        logging.info(f"Conectando a {servidor}:{puerto}...")
        client.connect(servidor, puerto)
        client.publish(topico, str(payload))
        client.disconnect()
        return True
    except Exception as e:
        logging.error(f"Error MQTT: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar_mqtt', methods=['POST'])
def enviar_mqtt():
    mac_node = request.form.get("mac_node")
    accion = request.form.get("accion")

    if not mac_node:
        flash("Debes seleccionar o agregar una MAC valida")
        return redirect(url_for("index"))

    if accion == "destello":
        exito = publicar_mqtt(f"{mac_node}/destello", "destello")
        if exito:
            flash(f"Comando Destello enviado a {mac_node}")
        else:
            flash("Error al conectar con MQTT")
            
    elif accion == "setpoint":
        valor = request.form.get("setpoint_val")
        if not valor:
            flash("Debes indicar un valor para el Setpoint")
            return redirect(url_for("index"))
            
        exito = publicar_mqtt(f"{mac_node}/setpoint", valor)
        if exito:
            flash(f"Setpoint {valor} enviado a {mac_node}")
        else:
            flash("Error al conectar con MQTT")

    return redirect(url_for("index"))