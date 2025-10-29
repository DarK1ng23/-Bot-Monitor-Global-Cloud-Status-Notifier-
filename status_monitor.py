import os
import requests
import json
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from flask import Flask

# === FLASK PARA RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Monitor de servicios en ejecución"

# Cargar variables desde .env
load_dotenv()

# === CONFIGURACIÓN ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO = 1  # 15 minutos

SERVICIOS = {
    "AWS": "https://status.aws.amazon.com/data.json",
    "Azure": "https://status.azure.com/en-us/status",
    "Microsoft 365": "https://status.office.com/api/reporting/ServiceComms/CurrentStatus",
    "Google Cloud": "https://status.cloud.google.com/incidents.json",
    "Google Workspace": "https://www.google.com/appsstatus/dashboard/incidents.json"
}

PAGINAS_ESTADO = {
    "AWS": "https://status.aws.amazon.com/",
    "Azure": "https://status.azure.com/en-us/status",
    "Microsoft 365": "https://status.office.com/",
    "Google Cloud": "https://status.cloud.google.com/",
    "Google Workspace": "https://www.google.com/appsstatus/dashboard/"
}

ARCHIVO_ESTADO = "estado_servicios.json"

# === SESIÓN SEGURA ===
session = requests.Session()
retries = Retry(total=3, backoff_factor=2)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)


# === FUNCIONES ===
def enviar_notificacion(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": None}
    try:
        r = session.get(url, params=params, timeout=10)
        if r.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Notificación enviada.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error al enviar notificación: {r.text}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error al conectar con Telegram: {e}")


def cargar_estado_anterior():
    try:
        with open(ARCHIVO_ESTADO, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def guardar_estado_actual(estado):
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump(estado, f, indent=4)


def verificar_servicios():
    estado_anterior = cargar_estado_anterior()
    estado_actual = {}

    for nombre, url in SERVICIOS.items():
        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.text.lower()
                if any(x in data for x in ["degraded", "incident", "down", "outage", "disruption"]):
                    estado = "⚠️ Problemas detectados"
                else:
                    estado = "✅ Operativo"
            else:
                estado = "❌ Error al consultar"
        except Exception as e:
            estado = f"❌ Error: {str(e)}"

        estado_actual[nombre] = estado

        if nombre not in estado_anterior or estado != estado_anterior[nombre]:
            mensaje = (
                f"🚨 Cambio detectado en {nombre}\n"
                f"Anterior: {estado_anterior.get(nombre, 'Desconocido')}\n"
                f"Actual: {estado}\n"
                f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            if "⚠️" in estado or "❌" in estado:
                mensaje += f"\n🔗 Ver más: {PAGINAS_ESTADO[nombre]}"
            enviar_notificacion(mensaje)

    guardar_estado_actual(estado_actual)
    return estado_actual


def enviar_reporte_general(estado_actual):
    reporte = "📊 *REPORTE GENERAL DE ESTADO DE SERVICIOS:*\n\n"
    for servicio, estado in estado_actual.items():
        if "⚠️" in estado or "❌" in estado:
            reporte += f"• {servicio}: {estado}\n   🔗 {PAGINAS_ESTADO[servicio]}\n"
        else:
            reporte += f"• {servicio}: {estado}\n"
    reporte += f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    enviar_notificacion(reporte)


# === PROGRAMA PRINCIPAL ===
if __name__ == "__main__":
    print("🚀 MONITOR DE SERVICIOS INICIADO")
    enviar_notificacion("✅ Monitor de servicios iniciado correctamente.")

    # Iniciar Flask para Render
    port = int(os.environ.get("PORT", 10000))
    from threading import Thread

    def ejecutar_monitor():
        while True:
            resultado = verificar_servicios()
            enviar_reporte_general(resultado)
            hora = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{hora}] ESTADO ACTUAL:")
            for servicio, estado in resultado.items():
                print(f"   - {servicio}: {estado}")
            time.sleep(INTERVALO)

    # Hilo separado para el monitor
    Thread(target=ejecutar_monitor, daemon=True).start()

    app.run(host="0.0.0.0", port=port)  
