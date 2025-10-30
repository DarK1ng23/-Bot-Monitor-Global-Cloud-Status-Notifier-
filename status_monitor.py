import requests
import asyncio
from datetime import datetime
from telegram import Bot
from flask import Flask, send_from_directory
import os
import logging

# --- Configuración ---
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
CHAT_ID = "TU_CHAT_ID_AQUI"

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# --- Silenciar logs de Flask ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Solo errores graves

# URLs de estado
status_urls = {
    "AWS": "https://status.aws.amazon.com/",
    "Azure": "https://status.azure.com/en-us/status",
    "Microsoft 365": "https://status.office.com/",
    "Google Cloud": "https://status.cloud.google.com/",
    "Google Workspace": "https://www.google.com/appsstatus/dashboard/",
}

previous_status = {}

# --- Funciones de verificación ---
def verificar_servicio(nombre, url):
    try:
        response = requests.get(url, timeout=10)
        return "✅ Operativo" if response.status_code == 200 else "⚠️ Problemas detectados"
    except requests.exceptions.SSLError:
        return "❌ Error SSL"
    except Exception:
        return "⚠️ Problemas detectados"

def generar_alerta(nombre, estado, url):
    return f"🚨 Cambio detectado en *{nombre}*\n\nNuevo estado: {estado}\n🔗 {url}"

# --- Monitor asíncrono ---
async def monitorear():
    global previous_status
    while True:
        cambios = []
        reporte_general = "📊 REPORTE GENERAL DE ESTADO DE SERVICIOS:\n\n"

        for nombre, url in status_urls.items():
            estado_actual = verificar_servicio(nombre, url)
            estado_anterior = previous_status.get(nombre)

            reporte_general += f"• {nombre}: {estado_actual}\n"
            if estado_actual != "✅ Operativo":
                reporte_general += f"   🔗 {url}\n"

            if estado_anterior and estado_anterior != estado_actual:
                cambios.append(generar_alerta(nombre, estado_actual, url))

            previous_status[nombre] = estado_actual

        if cambios:
            for alerta in cambios:
                await bot.send_message(chat_id=CHAT_ID, text=alerta, parse_mode="Markdown")

        await bot.send_message(chat_id=CHAT_ID, text=reporte_general)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🕒 Próximo reporte en 15 minutos...")
        await asyncio.sleep(900)

# --- Rutas Flask ---
@app.route("/")
def home():
    return "✅ Bot Monitor Global Cloud Status corriendo correctamente."

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# --- Main ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # --- Manejar event loop moderno ---
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(monitorear())
    app.run(host="0.0.0.0", port=port)

