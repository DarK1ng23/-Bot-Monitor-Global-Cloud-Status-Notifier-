import os
import requests
import json
import time
import threading
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from flask import Flask

# === Cargar variables del entorno ===
load_dotenv()

# === CONFIGURACIÓN GENERAL ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO = int(os.getenv("INTERVALO", 900))  # 15 min por defecto

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

# === SESIÓN DE REQUESTS CON RETRIES ===
session = requests.Session()
retries = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

# === SERVIDOR FLASK ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Monitor activo y corriendo correctamente", 200


# === FUNCIONES ===
def enviar_notificacion(mensaje: str):
    """Envía una notificación al bot de Telegram."""
    if not TOKEN or not CHAT_ID:
        print("❌ Faltan variables de entorno TELEGRAM_TOKEN o CHAT_ID.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        r = session.get(url, params=params, timeout=10)
        if r.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Notificación enviada.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error al enviar notificación: {r.text}")
    except requests.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error al conectar con Telegram: {e}")


def cargar_estado_anterior() -> dict:
    """Carga el estado anterior desde el archivo JSON."""
    if os.path.exists(ARCHIVO_ESTADO):
        try:
            with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Archivo de estado dañado. Se reiniciará.")
            return {}
    return {}


def guardar_estado_actual(estado: dict):
    """Guarda el estado actual en un archivo JSON."""
    try:
        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Error al guardar estado actual: {e}")


def analizar_estado(nombre: str, data: str, status_code: int) -> str:
    """Determina el estado del servicio según la respuesta."""
    if status_code != 200:
        return "❌ Error al consultar"

    palabras_clave = ["degraded", "incident", "down", "outage", "disruption"]
    return "⚠️ Problemas detectados" if any(p in data.lower() for p in palabras_clave) else "✅ Operativo"


def verificar_servicios() -> dict:
    """Verifica el estado de los servicios y envía notificaciones si hay cambios."""
    estado_anterior = cargar_estado_anterior()
    estado_actual = {}

    for nombre, url in SERVICIOS.items():
        try:
            resp = session.get(url, timeout=10)
            estado = analizar_estado(nombre, resp.text, resp.status_code)
        except requests.RequestException as e:
            estado = f"❌ Error: {e}"

        estado_actual[nombre] = estado

        # Detectar cambios
        if estado != estado_anterior.get(nombre):
            mensaje = (
                f"🚨 *Cambio detectado en {nombre}*\n"
                f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Anterior: {estado_anterior.get(nombre, 'Desconocido')}\n"
                f"Actual: {estado}\n"
            )
            if "⚠️" in estado or "❌" in estado:
                mensaje += f"🔗 [Ver más]({PAGINAS_ESTADO[nombre]})"
            enviar_notificacion(mensaje)

    guardar_estado_actual(estado_actual)
    return estado_actual


def enviar_reporte_general(estado_actual: dict):
    """Envía un reporte completo del estado de los servicios."""
    reporte = "📊 *REPORTE GENERAL DE ESTADO DE SERVICIOS:*\n\n"
    for servicio, estado in estado_actual.items():
        if "⚠️" in estado or "❌" in estado:
            reporte += f"• {servicio}: {estado}\n   🔗 [Ver más]({PAGINAS_ESTADO[servicio]})\n"
        else:
            reporte += f"• {servicio}: {estado}\n"

    reporte += f"\n🕒 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    enviar_notificacion(reporte)


def loop_monitoreo():
    """Ejecuta el monitoreo de servicios en bucle."""
    print("🚀 MONITOR DE SERVICIOS INICIADO")
    enviar_notificacion("✅ *Monitor de servicios iniciado correctamente.*")

    while True:
        resultado = verificar_servicios()
        enviar_reporte_general(resultado)

        hora = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{hora}] ESTADO ACTUAL:")
        for servicio, estado in resultado.items():
            print(f"   - {servicio}: {estado}")

        time.sleep(INTERVALO)


if __name__ == "__main__":
    # Iniciar monitoreo en un hilo paralelo para que Flask siga corriendo
    hilo = threading.Thread(target=loop_monitoreo, daemon=True)
    hilo.start()

    # Render necesita un puerto abierto
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
